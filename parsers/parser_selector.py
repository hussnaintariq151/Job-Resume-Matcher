# app/parsers/parser_selector.py

from .pdf_parser import extract_text_from_pdf
from .scanned_pdf_parser import extract_text_from_scanned_pdf

def extract_text(file_path: str, mode: str = "regular") -> str:
    if mode == "regular":
        return extract_text_from_pdf(file_path)
    elif mode == "scanned":
        return extract_text_from_scanned_pdf(file_path)
    else:
        raise ValueError("Invalid mode. Use 'regular' or 'scanned'.")
