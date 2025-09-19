import os, sys, json, re
import fitz  # PyMuPDF
import pdfplumber
import camelot
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import pytesseract
from tqdm import tqdm

HEADER_KEYWORDS = {"MONTHLY", "FACTSHEET", "PAGE", "JUNE", "MAY"}
MIN_TABLE_NUMERIC_FRAC = 0.15
TOP_HEADER_SKIP_RATIO = 0.12
GRID_BUCKET_WIDTH = 18.0

def norm_text(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split())

def looks_like_number(s: str) -> bool:
    if s is None: return False
    s2 = re.sub(r'[,\s%₹]', '', str(s))
    try:
        float(s2)
        return True
    except:
        return False

def parse_number(s: str):
    if s is None: return None
    s2 = re.sub(r'[,\s%₹]', '', str(s))
    try:
        return float(s2) if '.' in s2 else int(float(s2))
    except:
        return s

def bbox_area(b):
    if not b: return 0
    return max(0.0, (b[2]-b[0])*(b[3]-b[1]))

def rect_intersect_area(a,b):
    if not a or not b: return 0
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0: return 0
    return (x1-x0)*(y1-y0)

def extract_spans(doc: fitz.Document, p_idx:int):
    page = doc.load_page(p_idx)
    d = page.get_text("dict")
    spans=[]
    for block in d.get("blocks", []):
        if block.get("type") != 0: 
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                txt = span.get("text","").strip()
                if not txt: continue
                bbox = tuple(span.get("bbox",(0,0,0,0)))
                size = float(span.get("size",0))
                spans.append({"text":norm_text(txt),"bbox":bbox,"size":size})
    spans.sort(key=lambda s:(s["bbox"][1], s["bbox"][0]))
    return spans

def group_spans_to_blocks(spans, y_tol=4.0):
    if not spans: return []
    blocks=[]
    cur={"spans":[spans[0]],"bbox":spans[0]["bbox"]}
    for sp in spans[1:]:
        prev=cur["spans"][-1]
        gap = sp["bbox"][1]-prev["bbox"][3]
        if gap <= y_tol:
            cur["spans"].append(sp)
            x0=min(cur["bbox"][0], sp["bbox"][0]); y0=min(cur["bbox"][1], sp["bbox"][1])
            x1=max(cur["bbox"][2], sp["bbox"][2]); y1=max(cur["bbox"][3], sp["bbox"][3])
            cur["bbox"]=(x0,y0,x1,y1)
        else:
            blocks.append(cur)
            cur={"spans":[sp],"bbox":sp["bbox"]}
    blocks.append(cur)
    out=[]
    for b in blocks:
        text=" ".join(s["text"] for s in b["spans"]).strip()
        sizes=[s["size"] for s in b["spans"] if s.get("size")]
        out.append({"text":text,"bbox":b["bbox"],"font_size":float(np.median(sizes)) if sizes else None})
    return out

def classify_blocks(blocks):
    sizes=[b["font_size"] for b in blocks if b.get("font_size")]
    median_size = float(np.median(sizes)) if sizes else 10.0
    header_thresh = max(median_size*1.15, median_size+0.5)
    paras=[]
    current_section=None
    for b in sorted(blocks,key=lambda x:(x["bbox"][1],-(x.get("font_size") or 0))):
        txt=b["text"].strip()
        if not txt: continue
        is_heading = (b.get("font_size") or 0)>=header_thresh or (len(txt)<=80 and txt.isupper())
        if is_heading:
            current_section=txt.title()
            paras.append({"type":"paragraph","section":current_section,"sub_section":None,"text":txt,"bbox":b["bbox"]})
        else:
            paras.append({"type":"paragraph","section":current_section,"sub_section":None,"text":txt,"bbox":b["bbox"]})
    return paras

# ---------------- TABLES ----------------
def clean_table(raw):
    t=[[str(c or "").strip() for c in row] for row in raw]
    if not t: return t
    max_cols=max(len(r) for r in t)
    t=[r+[""]*(max_cols-len(r)) for r in t]
    last=-1
    for c in range(max_cols):
        for r in t:
            if r[c].strip():
                last=c; break
    if last==-1: return []
    t=[r[:last+1] for r in t]
    # merge multi-row headers
    if len(t)>=2:
        n0=sum(1 for x in t[0] if x); n1=sum(1 for x in t[1] if x)
        if n0<n1:
            merged=[]
            for i in range(len(t[1])):
                a=t[0][i] if i<len(t[0]) else ""
                b=t[1][i] if i<len(t[1]) else ""
                merged.append(((a+" "+b).strip()) if a and b and a!=b else a or b)
            t=[merged]+t[2:]
    return t

def is_table_valid(t, min_numeric_frac=MIN_TABLE_NUMERIC_FRAC):
    if not t or not any(t): return False
    cells=[c for row in t for c in row]
    num_numeric=sum(1 for c in cells if looks_like_number(str(c)))
    frac=num_numeric/max(1,len(cells))
    return frac>=min_numeric_frac

def extract_tables(pl_page):
    tables=[]
    # 1) Camelot
    try:
        camel_tables = camelot.read_pdf(pl_page.pdf_path, flavor='stream', pages=str(pl_page.page_number))
        for t in camel_tables:
            df=t.df
            cl = clean_table(df.values.tolist())
            if is_table_valid(cl):
                tables.append(cl)
    except:
        pass
    # 2) pdfplumber fallback
    try:
        for tbl in pl_page.extract_tables():
            cl=clean_table(tbl)
            if is_table_valid(cl):
                tables.append(cl)
    except:
        pass
    return tables

# ---------------- CHARTS ----------------
def detect_vector_charts(doc, p_idx, text_blocks):
    page=doc.load_page(p_idx)
    drawings=page.get_drawings() or []
    tbboxes=[(b["bbox"],b["text"]) for b in text_blocks]
    charts=[]
    page_h=page.rect.height
    for d in drawings:
        rect=d.get("rect")
        if not rect: continue
        rect=tuple(rect)
        w,h=rect[2]-rect[0], rect[3]-rect[1]
        if w<40 or h<40: continue
        if rect[1]<page_h*TOP_HEADER_SKIP_RATIO: continue
        # collect nearby text
        intersecting=[]
        for tb,txt in tbboxes:
            if rect_intersect_area(tb,rect)>0 or rect_intersect_area(tb,(rect[0]-6,rect[1]-6,rect[2]+6,rect[3]+6))>0:
                if any(k in txt.upper() for k in HEADER_KEYWORDS): continue
                intersecting.append({"bbox":tb,"text":txt})
        if not intersecting: continue
        # parse year-value pairs
        year_pairs=[]
        for it in intersecting:
            s=it["text"].strip()
            tokens=re.split(r'[\s,;]+', s)
            for i in range(len(tokens)-1):
                a=tokens[i]; b=tokens[i+1]
                if re.match(r'^(FY|FY-)?\d{2,4}E?$', a.upper()) and looks_like_number(b):
                    year_pairs.append((a,b))
        chart_data=None
        if year_pairs:
            chart_data=[["label","value"]]+[[a,parse_number(b)] for a,b in year_pairs]
        charts.append({"type":"chart","section":None,"sub_section":None,"description":"Vector chart","bbox":rect,"legend":[],"chart_data":chart_data})
    return charts

def parse_pdf(pdf_path:str, csv_dir=None):
    if not os.path.exists(pdf_path): raise FileNotFoundError(pdf_path)
    doc=fitz.open(pdf_path)
    pl=pdfplumber.open(pdf_path)
    result={"pages":[]}
    for p_idx in tqdm(range(doc.page_count), desc="Parsing PDF"):
        page_out={"page_number":p_idx+1,"content":[]}
        # paragraphs
        spans=extract_spans(doc,p_idx)
        blocks=group_spans_to_blocks(spans)
        paragraphs=classify_blocks(blocks)
        # tables
        try: pl_page=pl.pages[p_idx]; tables=extract_tables(pl_page)
        except: tables=[]
        for t in tables:
            page_out["content"].append({"type":"table","section":None,"sub_section":None,"description":"Table","table_data":t})
            if csv_dir:
                try:
                    os.makedirs(csv_dir,exist_ok=True)
                    df=pd.DataFrame(t[1:],columns=t[0]) if len(t)>1 else pd.DataFrame(t)
                    df.to_csv(os.path.join(csv_dir,f"page{p_idx+1}_table.csv"),index=False)
                except: pass
        # charts
        charts=detect_vector_charts(doc,p_idx,blocks)
        page_out["content"].extend(charts)
        # add paragraphs (skip overlapping with tables/charts)
        chart_table_bboxes=[it.get("bbox") for it in page_out["content"] if it.get("bbox")]
        for p in paragraphs:
            skip=False; pb=p.get("bbox")
            if pb:
                for cb in chart_table_bboxes:
                    if not cb: continue
                    if rect_intersect_area(pb,cb)/max(1.0,bbox_area(pb))>0.6:
                        skip=True; break
            if not skip:
                page_out["content"].append({"type":"paragraph","section":p.get("section"),"sub_section":p.get("sub_section"),"text":p.get("text")})
        result["pages"].append(page_out)
    pl.close(); doc.close()
    return result

# ---------------- CLI ----------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", help="Path to input PDF")
    parser.add_argument("output_json", help="Path to output JSON file")
    parser.add_argument("--csv-dir", default=None, help="Optional directory to save table CSVs")
    args = parser.parse_args()

    out = parse_pdf(args.input_pdf, csv_dir=args.csv_dir)

    # Save JSON
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Print sample preview (first page, first few items)
    print("\n[INFO] Parsing complete. JSON written to:", args.output_json)
    if out["pages"]:
        print("\n--- Sample Output Preview ---")
        first_page = out["pages"][0]
        print(f"Page {first_page['page_number']}:")
        for item in first_page["content"][:5]:
            print(json.dumps(item, indent=2, ensure_ascii=False))
