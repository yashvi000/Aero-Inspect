# Converting embed text chunks into vector representations
# The model is loaded once and cached globally

from sentence_transformers import SentenceTransformer
from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

logger = get_logger("retrieval")

_model = None


def _get_model_name() -> str:
    config = get_yaml_config()
    return config["ingestion"]["embedding_model"]


def _load_model() -> SentenceTransformer:
    # Loading and caching the embedding model
    
    global _model
    if _model is not None:
        return _model

    model_name = _get_model_name()
    logger.info(f"Loading embedding model: {model_name}")
    _model = SentenceTransformer(model_name)
    logger.info(f"Embedding model loaded: {model_name}")

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    # Converting list of text strings into vector embeddings

    if not texts:
        logger.warning("Empty text list received for embedding")
        return []

    model = _load_model()
    embeddings = model.encode(texts, show_progress_bar=False)

    logger.info(f"Embedded {len(texts)} texts into {len(embeddings[0])}-dim vectors")

    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    # Converting one text string into vector embedding

    if not text or not text.strip():
        logger.warning("Empty text received for embedding")
        return []

    model = _load_model()
    embedding = model.encode(text, show_progress_bar=False)

    return embedding.tolist()