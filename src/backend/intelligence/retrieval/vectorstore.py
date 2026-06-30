# Managing Chroma vector database for document storage and semantic search
import chromadb

from src.shared.utils.logging import get_logger
from src.shared.utils.paths import PROJECT_ROOT
from src.backend.core.settings import get_yaml_config

logger = get_logger("retrieval")

_client = None
_collection = None


def _get_retrieval_config() -> dict:
    config = get_yaml_config()
    return config["retrieval"]


def _get_persist_path() -> str:
    config = _get_retrieval_config()
    relative_path = config["persist_directory"]
    return str(PROJECT_ROOT / relative_path)


def _get_collection_name() -> str:
    return _get_retrieval_config()["collection_name"]


def get_client() -> chromadb.PersistentClient:
    # Creating a persistent Chroma client, cached globally.
    
    global _client

    if _client is not None:
        return _client

    persist_path = _get_persist_path()
    logger.info(f"Initializing Chroma client at: {persist_path}")
    _client = chromadb.PersistentClient(path=persist_path)

    return _client


def get_collection() -> chromadb.Collection:
    # Creating document collection, cached globally

    global _collection

    if _collection is not None:
        return _collection

    client = get_client()
    collection_name = _get_collection_name()

    _collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    logger.info(
        f"Collection '{collection_name}' ready. "
        f"Current count: {_collection.count()}"
    )

    return _collection


def add_chunks(
    ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    # Adding chunks to the vector store.

    collection = get_collection()

    batch_size = _get_retrieval_config()["chunk_batch_size"]
    total = len(ids)

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)

        collection.add(
            ids=ids[start:end],
            documents=texts[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

        logger.info(f"Added chunks {start + 1} to {end} | Total : {total}")

    logger.info(
        f"Total chunks in collection: {collection.count()}"
    )


def query_by_embedding(
    query_embedding: list[float],
    top_k: int = None,
    where_filter: dict = None,
) -> list[dict]:
    # Searching the vector store using query embedding

    collection = get_collection()
    config = _get_retrieval_config()

    if top_k is None:
        top_k = config["top_k"]

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }

    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    # Converting Chroma output into list of dicts
    # lower similarity distance -> more similar
    output = []
    if results and results["documents"]:
        for i in range(len(results["documents"][0])):
            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

    logger.info(
        f"Query Results : {len(output)} | "
        f"top_k={top_k}, filter={where_filter}"
    )
    return output


def get_collection_stats() -> dict:

    collection = get_collection()
    return {
        "total_chunks": collection.count(),
        "collection_name": _get_collection_name(),
    }


def reset_collection() -> None:
    # To delete and recreate the collection
    # Used by reset_demo.py and rebuild scripts

    client = get_client()
    collection_name = _get_collection_name()

    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted collection: {collection_name}")
    except Exception:
        logger.info(f"Collection {collection_name} did not exist")

    global _collection
    _collection = None

    get_collection()
    logger.info(f"Recreated collection: {collection_name}")