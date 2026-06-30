"""
One-time script to ingest all corpus documents, embed them, and store in 
Chroma.
"""

import sys
sys.path.append(".")

from src.shared.utils.logging import get_logger
from src.backend.intelligence.ingestion.indexer import ingest_all
from src.backend.intelligence.retrieval.embedder import embed_texts
from src.backend.intelligence.retrieval.vectorstore import (
    reset_collection,
    add_chunks,
    get_collection_stats,
)

logger = get_logger("retrieval")


def main():
    logger.info("Starting vector store build")

    # Ingesting all documents
    logger.info("Ingesting documents ...")
    chunks = ingest_all()

    if not chunks:
        logger.error("No chunks produced")
        return

    # Reseting existing collection
    logger.info("Resetting vector store ...")
    reset_collection()

    # Preparing data for Chroma
    logger.info("Preparing chunks for embedding ...")
    ids = []
    texts = []
    metadatas = []

    for _, chunk in enumerate(chunks):
        
        chunk_id = f"{chunk.metadata['source']}_{chunk.metadata['document_id']}_{chunk.metadata['chunk_index']}"
        ids.append(chunk_id)
        texts.append(chunk.text)

        # Validating Chroma metadata data type
        clean_metadata = {}
        for key, value in chunk.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            else:
                clean_metadata[key] = str(value)

        metadatas.append(clean_metadata)

    # Embedding all texts
    logger.info(f"Embedding {len(texts)} chunks ...")
    embeddings = embed_texts(texts)

    if len(embeddings) != len(texts):
        logger.error(
            f"Embedding count mismatch: "
            f"{len(embeddings)} embeddings for {len(texts)} texts"
        )
        return

    # Storing in Chroma
    logger.info("Storing in Chroma ...")

    add_chunks(
        ids=ids,
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    stats = get_collection_stats()
    logger.info(f"Build complete | Stats: {stats}")


if __name__ == "__main__":
    main()