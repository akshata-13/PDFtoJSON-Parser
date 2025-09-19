📄 PDF to JSON Parser
📌 Overview

This project provides a Python-based PDF parsing tool with both a command-line interface (CLI) and a Streamlit dashboard.
It converts unstructured PDF documents into a well-organized JSON format, preserving page hierarchy and distinguishing between paragraphs, tables, and charts for easier downstream analysis.:

✨ Features

📑 Page-wise extraction with page_number

📝 Paragraph grouping with section/sub-section detection using font size & heuristics

📊 Table extraction via Camelot and pdfplumber, normalized into 2D arrays

📈 Chart/vector detection with bounding boxes and optional OCR hook for labels

🗂️ Outputs clean, structured JSON preserving hierarchy

🌐 Streamlit Dashboard for PDF upload and JSON download

⚙️ Installation

Ensure you have Python 3.9+ installed

(Recommended) Use a virtual environment

Install dependencies:

pip install -r requirements.txt


🖥️ Usage
1️⃣ CLI Mode

Run the parser directly from terminal:

python app.py input.pdf output.json 


input.pdf → Path to input PDF

output.json → Output JSON file path


2️⃣ Streamlit Dashboard

Run the interactive web app:

streamlit run dashboard.py


⚠️ Notes & Limitations

Heading detection uses font-size heuristics → may require tuning for unusual PDFs

Complex or image-based tables may not extract perfectly

OCR is optional and disabled by default

Charts without text labels may only return bounding boxes
