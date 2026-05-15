"""
Singleton embedding service using sentence-transformers.
Loads the model once and reuses for all encoding requests.
"""

import threading
from typing import List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_model = None
_lock = threading.Lock()


def get_embedding_model():
    """Thread-safe singleton loader for the embedding model."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model", model=settings.EMBEDDING_MODEL)
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info("Embedding model loaded")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Encode a list of strings into embeddings.
    Returns a list of 384-dim float vectors.
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # unit vectors for cosine similarity
    )
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Encode a single query string."""
    return embed_texts([query])[0]
