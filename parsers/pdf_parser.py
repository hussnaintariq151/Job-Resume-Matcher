import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return clean_text(text)

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()
