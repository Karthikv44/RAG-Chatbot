"""
Cross-encoder re-ranker using ms-marco-MiniLM-L-6-v2.
Scores each retrieved chunk against the query and returns top-k.
Runs locally — no API key needed.
"""

from functools import lru_cache

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from Src.Loggers.logger import get_logger

logger = get_logger(__name__)

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache
def get_reranker() -> CrossEncoder:
    logger.info(f"Loading cross-encoder: {MODEL_NAME}")
    return CrossEncoder(MODEL_NAME)


def rerank(query: str, documents: list[Document], top_k: int = 5) -> list[Document]:
    """Score all docs against query and return top_k by relevance."""
    if not documents:
        return []

    reranker = get_reranker()
    pairs = [(query, doc.page_content) for doc in documents]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
    top = [doc for _, doc in ranked[:top_k]]

    logger.info(f"Re-ranked {len(documents)} docs → top {len(top)}")
    return top
