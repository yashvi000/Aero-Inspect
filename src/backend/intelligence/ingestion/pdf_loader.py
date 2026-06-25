import logging
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFLoadError(Exception):
    # Raised when PDF text extraction fails
    pass


def load_pdf(file_path: str) -> str:
    # Extracts all text from PDF files
    
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected .pdf, got: {path.suffix}")

    try:
        doc = fitz.open(str(path))
    except Exception as e:
        raise PDFLoadError(f"Failed to open PDF {path.name}: {e}")

    pages_text = []
    for page in doc:
        text = page.get_text(sort=True)
        if text.strip():
            pages_text.append(text.strip())

    doc.close()
    full_text = "\n\n".join(pages_text)

    if not full_text.strip():
        logger.warning(f"No text extracted from PDF: {path.name}")
        return ""

    logger.info(f"Extracted {len(full_text)} chars from PDF: {path.name}")
    return full_text