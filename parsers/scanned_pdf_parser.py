

import pytesseract
from pdf2image import convert_from_path
import re

# Required for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_scanned_pdf(file_path: str) -> str:
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return clean_text(text)

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()
