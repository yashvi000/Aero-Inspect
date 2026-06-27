from collections import Counter

from src.shared.utils.paths import CORPUS_DIR
from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

from src.backend.intelligence.ingestion.pdf_loader import load_pdf
from src.backend.intelligence.ingestion.xml_loader import load_xml
from src.backend.intelligence.ingestion.html_loader import load_html
from src.backend.intelligence.ingestion.chunker import chunk_document, Chunk

logger = get_logger("ingestion")

LOADER_MAP = {
    ".pdf": load_pdf,
    ".xml": load_xml,
    ".html": load_html,
    ".htm": load_html,
}


def _get_ingestion_config() -> dict:
    return get_yaml_config()["ingestion"]


def _get_source_map() -> dict:
    return _get_ingestion_config()["source_map"]


def _get_supported_extensions() -> set:
    return set(_get_ingestion_config()["supported_extensions"])


def _get_aircraft_type() -> str:
    return _get_ingestion_config()["aircraft_type"]


def _get_defect_keywords() -> dict:
    return _get_ingestion_config()["defect_keywords"]


def _detect_defect_type(filename: str, text: str) -> str:
    
    keywords_map = _get_defect_keywords()
    filename_lower = filename.lower()
    text_sample = text[:3000].lower()

    for defect_type, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in filename_lower or keyword in text_sample:
                return defect_type

    return "general"


def _get_loader(file_path):
    return LOADER_MAP.get(file_path.suffix.lower())


def _get_corpus_files(folder_path):
    
    supported_extensions = _get_supported_extensions()

    if not folder_path.exists():
        return []

    return sorted([
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ])


def _process_file(file_path, source_type: str) -> list[Chunk]:
    
    loader = _get_loader(file_path)

    if loader is None:
        logger.warning(f"Skipping unsupported file: {file_path.name}")
        return []

    try:
        text = loader(str(file_path))
    except Exception as e:
        logger.error(f"Failed to load {file_path.name}: {e}")
        return []

    if not text.strip():
        logger.warning(f"Empty text from file: {file_path.name}")
        return []

    defect_type = _detect_defect_type(file_path.name, text)

    metadata = {
        "source": source_type,
        "document_id": file_path.stem,
        "aircraft_type": _get_aircraft_type(),
        "defect_type": defect_type,
        "file_name": file_path.name,
    }

    return chunk_document(text, metadata)


def ingest_folder(folder_name: str) -> list[Chunk]:
    source_map = _get_source_map()

    if folder_name not in source_map:
        logger.error(f"Folder {folder_name} not found in source_map")
        return []

    source_type = source_map[folder_name]
    folder_path = CORPUS_DIR / folder_name
    files = _get_corpus_files(folder_path)

    if not files:
        logger.warning(f"No supported files found in {folder_name}/")
        return []

    logger.info(f"Processing {folder_name}/ with {len(files)} files")

    folder_chunks = []
    for file_path in files:
        chunks = _process_file(file_path, source_type)
        folder_chunks.extend(chunks)

        if chunks:
            logger.info(
                f"{file_path.name}: {len(chunks)} chunks, "
                f"source={source_type}, "
                f"defect={chunks[0].metadata['defect_type']}"
            )

    return folder_chunks


def _print_summary(all_chunks: list[Chunk], total_files: int) -> None:
    source_counts = Counter()
    defect_counts = Counter()

    for chunk in all_chunks:
        source_counts[chunk.metadata["source"]] += 1
        defect_counts[chunk.metadata["defect_type"]] += 1

    logger.info("Ingestion Complete")
    logger.info(f"Files processed: {total_files}")
    logger.info(f"Total chunks: {len(all_chunks)}")

    logger.info("Chunks by source:")
    for source, count in sorted(source_counts.items()):
        logger.info(f"\t{source}: {count}")

    logger.info("Chunks by defect type:")
    for defect, count in sorted(defect_counts.items()):
        logger.info(f"\t{defect}: {count}")


def ingest_all() -> list[Chunk]:
    source_map = _get_source_map()
    all_chunks = []
    total_files = 0

    for folder_name in source_map.keys():
        folder_path = CORPUS_DIR / folder_name

        if not folder_path.exists():
            logger.warning(f"Skipping missing folder: {folder_name}/")
            continue

        files = _get_corpus_files(folder_path)
        total_files += len(files)

        chunks = ingest_folder(folder_name)
        all_chunks.extend(chunks)

    _print_summary(all_chunks, total_files)
    return all_chunks