📄 PDF to JSON Parser
📌 Overview

This project provides a Python-based PDF parsing tool with both a command-line interface (CLI) and a Streamlit dashboard.
It converts unstructured PDF documents into a well-organized JSON format, preserving page hierarchy and distinguishing between paragraphs, tables, and charts for easier downstream analysis.

✨ Features

📑 Page-wise extraction with page_number

📝 Paragraph grouping with section/sub-section detection using font size & heuristics

📊 Table extraction using Camelot and pdfplumber, normalized into 2D arrays

📈 Chart/vector detection with bounding boxes and optional OCR hook for labels

🗂️ Outputs clean, well-structured JSON preserving hierarchy

🌐 Streamlit Dashboard for PDF upload and JSON download

⚙️ Installation

Ensure you have Python 3.9+ installed

(Recommended) Create and activate a virtual environment

Install dependencies:

pip install -r requirements.txt

🔹 Optional OCR Support

If your PDFs contain scanned images and you want OCR text extraction:

macOS → brew install tesseract

Ubuntu/Debian → sudo apt-get install -y tesseract-ocr

🖥️ Usage
1️⃣ CLI Mode

Run the parser from terminal:

python app.py input.pdf output.json --csv-dir tables/


input.pdf → Path to input PDF

output.json → Output JSON file path

--csv-dir DIR → (optional) Export detected tables as CSVs

2️⃣ Streamlit Dashboard


streamlit run dashboard.py

