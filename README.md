# 📄 PDF to JSON Parser  

## 📌 Overview  
This project is a **Python-based PDF parsing system** that:  

- 📑 Extracts **paragraphs, tables, and charts** from PDF documents  
- 🗂️ Preserves **page-level hierarchy** and section/sub-section mapping  
- 📊 Converts tables into **structured 2D arrays**  
- 📈 Detects **vector charts/images** with bounding boxes and metadata  
- 🌐 Provides both a **CLI tool** and a **Streamlit dashboard** for ease of use  

---

## 🛠️ Features  

- 📄 **Page-wise extraction** with `page_number`  
- 📝 **Paragraph grouping** with font-size based heading/section detection  
- 📊 **Table extraction** using Camelot + pdfplumber fallback  
- 📈 **Chart/vector block detection** with optional OCR hook for labels  
- 🗂️ Outputs **clean, hierarchical JSON** preserving structure  
- 🌐 **Streamlit Dashboard** → Upload PDF & download JSON interactively  

---

## 🏗️ Project Architecture  

- **Text Extraction** → Extract spans & group into paragraphs  
- **Heading Detection** → Uses font size + heuristics for section/sub-sections  
- **Table Extraction** → Camelot (stream) + pdfplumber fallback, cleaned into 2D arrays  
- **Chart Detection** → Vector drawings + bounding boxes, year-value pairs parsed  
- **JSON Assembly** → Combines paragraphs, tables, and charts into structured output  
- **Dashboard** → Streamlit app for file upload, preview, and download  

---

## 🔧 Installation

1. Ensure you have **Python 3.9+** installed
2. (Recommended) Create a **virtual environment**
3. Install dependencies:

```bash
pip install -r requirements.txt
```
---

## ▶️ Usage

### 1️⃣ CLI Mode

```bash
python app.py input.pdf output.json 
```

* `input.pdf` → Path to input PDF
* `output.json` → Output JSON file path

---

### 2️⃣ Streamlit Dashboard

```bash
streamlit run dashboard.py
```
---



---

## ⚠️ Notes & Limitations

* Heading detection is **heuristic (font-size based)** → may need tuning
* Complex or scanned tables may not extract perfectly
* OCR support is **optional** and off by default
* Charts without text labels may only return bounding boxes

---
 

Do you want me to also add a **“Deployment” section** (Streamlit Cloud + Hugging Face Spaces) at the bottom so your faculty can run it online without setup?
```
