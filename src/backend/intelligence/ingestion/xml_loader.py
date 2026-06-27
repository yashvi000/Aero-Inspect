import logging
from pathlib import Path
import yaml
from lxml import etree

from src.shared.utils.paths import CONFIG_DIR
from src.shared.utils.logging import get_logger

logger = get_logger("ingestion")

class XMLLoadError(Exception):
    # Raised when XML parsing fails
    pass


def _get_xml_config() -> dict:
    
    config_path = CONFIG_DIR / "config.yaml"
    
    defaults = {
        "content_tags": ["P", "HD", "FP", "E", "SUM", "DATES", "EXTRACT", "AMDPAR"],
        "skip_tags": ["FRDOC", "BILCOD", "GPH", "FTNT"]
    }
    
    try:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("ingestion", {}).get("xml_tags", defaults)
    
    except Exception:
        return defaults


def load_xml(file_path: str) -> str:
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"XML not found: {file_path}")
    
    if path.suffix.lower() != ".xml":
        raise ValueError(f"Expected .xml, got: {path.suffix}")

    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError as e:
        raise XMLLoadError(f"Failed to parse XML {path.name}: {e}")

    cfg = _get_xml_config()
    skip_tags = set(cfg.get("skip_tags", []))
    text_parts = []

    def _extract(element):
        if element.tag in skip_tags:
            return
        
        if element.text and element.text.strip():
            text_parts.append(element.text.strip())
        
        for child in element:
            _extract(child)
            
            if child.tail and child.tail.strip():
                text_parts.append(child.tail.strip())

    _extract(tree.getroot())
    full_text = "\n".join(text_parts)

    if not full_text.strip():
        logger.warning(f"No text extracted from XML: {path.name}")
        return ""

    logger.info(f"Extracted {len(full_text)} chars from XML: {path.name}")
    return full_text