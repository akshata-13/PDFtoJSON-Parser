# PDF to JSON Parser

This project provides a Python-based PDF parsing tool with both a command-line interface and a Streamlit dashboard.
It converts unstructured PDF documents into a well-organized JSON format, preserving page hierarchy and distinguishing between paragraphs, tables, and charts for easier downstream analysis.

Live:

🚀 Features

📑 Page-wise extraction with page_number

📝 Paragraph grouping with best-effort section/sub-section detection using font size & heuristics

📊 Table extraction via camelot and pdfplumber, normalized into 2D arrays

📈 Chart/vector detection with bounding boxes and optional OCR hook for labels

🗂️ Outputs clean, well-structured JSON preserving hierarchy

🖥️ Streamlit Dashboard for PDF upload and JSON download

⚙️ Installation

Ensure you have Python 3.9+ installed.

(Recommended) Use a virtual environment.

Install dependencies:

pip install -r requirements.txt


🖥️ Usage
CLI Mode

Run the parser directly:

python app.py input.pdf output.json 


Arguments:

input.pdf → Path to input PDF

output.json → Path to save structured JSON

Streamlit Dashboard


streamlit run dashboard.py


⚙️ How It Works (Pipeline)

Heading Inference → Extracts text spans with PyMuPDF; detects headings using font size thresholds & heuristics.

Paragraph Extraction → Groups nearby spans into coherent paragraphs, preserving reading order.

Section Mapping → Assigns paragraphs to their most recent section/sub-section heading.

Table Extraction → Uses camelot (stream mode) + pdfplumber fallback; normalizes into 2D arrays; exports CSV if requested.

Chart Detection → Detects vector drawings via PyMuPDF; extracts bounding boxes; optionally parses year-value pairs.

JSON Assembly → Outputs structured JSON with page_number, type, section, sub_section, and associated content.

⚠️ Notes & Limitations

Heading detection is heuristic and font-size based → may require tuning for atypical PDFs.

Complex or image-based tables may not extract perfectly (Camelot/Tabula limitations).

OCR support for images is optional and disabled by default.

Charts without text labels may not be parsed beyond bounding boxes.
