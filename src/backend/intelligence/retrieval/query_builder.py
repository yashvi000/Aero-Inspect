"""
Combines defect type, zone label, and optional description into a retrieval 
query string to find relevant documents
"""
import json
from src.shared.utils.logging import get_logger
from src.shared.utils.paths import PROJECT_ROOT
from src.backend.core.settings import get_yaml_config

logger = get_logger("retrieval")

_zone_data = None


def _get_aircraft_type() -> str:
    config = get_yaml_config()
    return config["ingestion"]["aircraft_type"]


def _get_defect_search_terms() -> dict:

    config = get_yaml_config()
    keywords = config["ingestion"]["defect_keywords"]

    return {
        defect_type: " ".join(word_list)
        for defect_type, word_list in keywords.items()
    }


def _load_zone_data() -> dict:
    # Loading zone definitions from zone_definitions.json, caching globally

    global _zone_data
    if _zone_data is not None:
        return _zone_data

    zone_file = PROJECT_ROOT / "src" / "shared" / "zone_definitions.json"

    if not zone_file.exists():
        logger.warning(f"Zone definitions not found: {zone_file}")
        _zone_data = {}
        return _zone_data

    with open(zone_file, "r", encoding="utf-8") as f:
        raw = json.safe_load(f) if hasattr(json, 'safe_load') else json.load(f)

    _zone_data = {}
    for zone in raw.get("zones", []):
        _zone_data[zone["id"]] = zone

    logger.info(f"Loaded {len(_zone_data)} zone definitions")
    return _zone_data


def _get_zone_search_terms(zone_id: str) -> str:
    # Geting search terms for a specific zone
    # Getting zone_label if search_terms field is not present
    
    zones = _load_zone_data()
    if zone_id not in zones:
        return ""

    zone = zones[zone_id]

    if "search_terms" in zone and zone["search_terms"]:
        terms = zone["search_terms"]
        if isinstance(terms, list):
            return " ".join(terms)
        return terms
    return zone.get("zone_label", "")


def build_query(
    defect_type: str,
    zone_id: str = None,
    zone_label: str = None,
    description: str = None,
) -> str:
    # Builds retrieval query string from defect info for vector search
    # defect_type: Detected defect class from YOLO

    aircraft = _get_aircraft_type()
    defect_terms_map = _get_defect_search_terms()
    defect_terms = defect_terms_map.get(defect_type, defect_type)

    query_parts = [aircraft, "fuselage", defect_terms]

    # Get zone-specific search terms from zone_definitions.json
    if zone_id:
        zone_terms = _get_zone_search_terms(zone_id)
        if zone_terms:
            query_parts.append(zone_terms)
    elif zone_label:
        query_parts.append(zone_label)

    if description and description.strip():
        query_parts.append(description.strip())
        
    query = " ".join(query_parts)

    logger.info(
        f"Built query: defect={defect_type}, "
        f"zone={zone_id or 'none'}, "
        f"query_length={len(query)}"
    )
    return query