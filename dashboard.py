import os
import json
import streamlit as st
from app import parse_pdf   # ✅ re-use your parser from app.py

st.set_page_config(page_title="PDF Parser Dashboard", layout="wide")
st.title("📄 PDF Factsheet Parser")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    # Save to temp file
    tmp_path = "tmp_upload.pdf"
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("Parsing PDF... Please wait ⏳")
    result = parse_pdf(tmp_path)

    st.success(f"✅ Parsing complete. Pages extracted: {len(result['pages'])}")

    # Show preview of first page
    st.subheader("Preview (first page)")
    if result["pages"]:
        st.json(result["pages"][0])

    # Allow JSON download
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="parsed_output.json",
        mime="application/json"
    )
