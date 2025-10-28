from pypdf import PdfReader
from typing import Union
from io import BytesIO

def extract_text_from_pdf(file: Union[str, BytesIO]) -> str:
    """
    Extracts all text from a given PDF file.
    Works with both file paths and file-like objects (BytesIO).
    """
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # skip None or blank pages
            text.append(page_text.strip())
    return "\n".join(text)
