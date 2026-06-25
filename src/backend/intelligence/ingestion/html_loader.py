import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLLoadError(Exception):
    # Raised when HTML parsing fails
    pass

REMOVE_ELEMENTS = ["script", "style", "nav", "footer", "header", "noscript", "iframe"]


def _clean_text(raw_text: str) -> str:
    return "\n".join(line.strip() for line in raw_text.split("\n") if line.strip())


def load_html(file_path: str) -> str:
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"HTML not found: {file_path}")
    
    if path.suffix.lower() not in (".html", ".htm"):
        raise ValueError(f"Expected .html/.htm, got: {path.suffix}")

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        raise HTMLLoadError(f"Failed to read HTML {path.name}: {e}")

    if not content.strip():
        return ""

    try:
        soup = BeautifulSoup(content, "html.parser")
    except Exception as e:
        raise HTMLLoadError(f"Failed to parse HTML {path.name}: {e}")

    for tag in REMOVE_ELEMENTS:
        for el in soup.find_all(tag):
            el.decompose()

    raw_text = soup.get_text(separator="\n", strip=True)
    full_text = _clean_text(raw_text)

    if not full_text:
        logger.warning(f"No text extracted from HTML: {path.name}")
        return ""

    logger.info(f"Extracted {len(full_text)} chars from HTML: {path.name}")
    return full_text