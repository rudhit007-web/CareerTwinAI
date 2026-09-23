"""Extract text from supported resume formats."""
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text(path: str, content_type: str | None = None) -> str:
    ext=Path(path).suffix.lower()
    if ext=='.pdf' or content_type=='application/pdf':
        reader=PdfReader(path)
        return '\n'.join((page.extract_text() or '') for page in reader.pages).strip()
    if ext=='.docx' or content_type=='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc=Document(path)
        return '\n'.join(p.text for p in doc.paragraphs).strip()
    if ext=='.txt' or content_type=='text/plain':
        return Path(path).read_text(encoding='utf-8', errors='ignore').strip()
    raise ValueError('Unsupported file type. Upload PDF, DOCX or TXT.')
