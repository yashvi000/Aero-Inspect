"""
Retrieval interface used by the agent

Takes defect information, builds query, embeds it,
searches vector store, and returns ranked results
with DGCA sources prioritized.
"""

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config
from src.backend.intelligence.retrieval.query_builder import build_query
from src.backend.intelligence.retrieval.embedder import embed_single
from src.backend.intelligence.retrieval.vectorstore import query_by_embedding

logger = get_logger("retrieval")


def _get_top_k() -> int:
    config = get_yaml_config()
    return config["retrieval"]["top_k"]


def _get_score_threshold() -> float:
    config = get_yaml_config()
    return config["retrieval"]["score_threshold"]


def _get_priority_order() -> dict:
    config = get_yaml_config()
    return config["retrieval"]["priority_order"]


def _prioritize_results(results: list[dict]) -> list[dict]:
    # Prioritizing DGCA sources as this project focuses on Indian domain

    def sort_key(result):
        source = result["metadata"].get("source", "")
        priority = _get_priority_order()
        priority = priority.get(source, 99)
        distance = result.get("distance", 1.0)
        return (priority, distance)

    return sorted(results, key=sort_key)


def search_chunks(
    defect_type: str,
    zone_id: str = None,
    zone_label: str = None,
    description: str = None,
    top_k: int = None,
    source_filter: str = None,
) -> list[dict]:
    """
    Searches the document store for chunks relevant to the defect found

    defect_type: Defect class from YOLO detection.
    source_filter: Optional source filter like "dgca_car" for only DGCA docs.
    """

    if top_k is None:
        top_k = _get_top_k()

    # Building query
    query = build_query(
        defect_type=defect_type,
        zone_id=zone_id,
        zone_label=zone_label,
        description=description,
    )

    # Embeding query
    query_embedding = embed_single(query)

    if not query_embedding:
        logger.error("Failed to embed query")
        return []

    # Building optional filter
    where_filter = None
    if source_filter:
        where_filter = {"source": source_filter}

    # Searching vector store
    results = query_by_embedding(
        query_embedding=query_embedding,
        top_k=top_k,
        where_filter=where_filter,
    )

    if not results:
        logger.warning(
            f"No results found for defect : {defect_type} | "
            f"zone : {zone_id}"
        )
        return []

    # Filtering by score threshold
    threshold = _get_score_threshold()
    filtered = [
        r for r in results
        if r.get("distance", 1.0) <= (1.0 - threshold)
    ]

    if not filtered:
        logger.warning(
            f"All results below score threshold | "
            f"({threshold}) for defect : {defect_type}"
        )
        filtered = results[:top_k]

    # Prioritizing DGCA sources
    prioritized = _prioritize_results(filtered)

    logger.info(
        f"Search complete: {len(prioritized)} results | "
        f"Defect : {defect_type} | "
        f"Zone : {zone_id or 'none'}"
    )

    for i, result in enumerate(prioritized[:3]):
        logger.info(
            f"Result {i + 1} - "
            f"source : {result['metadata'].get('source')} | "
            f"defect : {result['metadata'].get('defect_type')} | "
            f"distance : {result.get('distance', '?'):.4f}"
        )

    return prioritized