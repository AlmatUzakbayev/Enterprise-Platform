from pathlib import Path
from docx import Document as DocxDocument
import fitz
from langdetect import detect

def parse_document(file_path: str) -> dict:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        text, page_map = _parse_pdf(file_path)
    elif ext == ".docx":
        text, page_map = _parse_docx(file_path)
    elif ext == ".txt":
        text, page_map = _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return {
        "text": text,
        "page_map": page_map,
        "language": _detect_language(text),
        "file_type": ext.lstrip(".")
    }

def _parse_txt(file_path: str) -> tuple[str, list]:
    with open(file_path, "r", encoding="utf-8",errors="ignore") as f:
        text = f.read()
    return text, [(0, len(text), 1)]

def _parse_docx(file_path: str) -> tuple[str, list]:
    doc = DocxDocument(file_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text, [(0, len(text), 1)]

def _parse_pdf(file_path: str) -> tuple[str, list]:
    doc = fitz.open(file_path)
    full_text = ""
    page_map = []

    for page_num, page in enumerate(doc,start=1):
        start = len(full_text)
        text = page.get_text("text")
        full_text += text + "\n"
        end = len(full_text)
        page_map.append((start, end, page_num))

    doc.close()
    return full_text.strip(), page_map

def _detect_language(text: str) -> str:
    try:
        return detect(text[:500])
    except Exception:
        return "unknown"
