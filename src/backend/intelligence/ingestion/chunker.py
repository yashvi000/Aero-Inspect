from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

logger = get_logger("ingestion")


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


def _get_splitter() -> RecursiveCharacterTextSplitter:
    config = get_yaml_config()
    ingestion_cfg = config["ingestion"]

    return RecursiveCharacterTextSplitter(
        chunk_size=ingestion_cfg["chunk_size"],
        chunk_overlap=ingestion_cfg["chunk_overlap"],
        length_function=len,
        separators=ingestion_cfg["chunk_separators"],
    )


def chunk_document(text: str, metadata: dict) -> list[Chunk]:
    doc_id = metadata.get("document_id", "unknown")

    if not text or not text.strip():
        logger.warning(f"Empty text received for document : {doc_id}")
        return []

    splitter = _get_splitter()
    raw_chunks = splitter.split_text(text)

    if not raw_chunks:
        logger.warning(f"No chunks created for document : {doc_id}")
        return []

    total_chunks = len(raw_chunks)
    chunks = []

    for idx, chunk_text in enumerate(raw_chunks):
        chunk_metadata = {
            **metadata,
            "chunk_index": idx,
            "total_chunks": total_chunks,
        }
        chunks.append(Chunk(text=chunk_text, metadata=chunk_metadata))

    logger.info(
        f"Chunked {doc_id}: {total_chunks} chunks | "
        f"(source={metadata.get('source')}, defect={metadata.get('defect_type')})"
    )

    return chunks