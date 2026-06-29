import pdfplumber
import io

def parse_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file in memory.
    """
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
