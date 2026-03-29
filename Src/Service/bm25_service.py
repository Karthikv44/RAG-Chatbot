"""
BM25 keyword search service.
Builds index from all ChromaDB chunks on startup.
Refreshed after each new ingestion.
"""

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from Src.Database.chroma_client import COLLECTION_NAME, get_chroma_client
from Src.Loggers.logger import get_logger

logger = get_logger(__name__)


class BM25Index:
    def __init__(self) -> None:
        self._bm25: BM25Okapi | None = None
        self._docs: list[Document] = []

    def build(self, documents: list[Document]) -> None:
        self._docs = documents
        tokenized = [doc.page_content.lower().split() for doc in documents]
        self._bm25 = BM25Okapi(tokenized)
        logger.info(f"BM25 index built with {len(documents)} documents")

    def search(self, query: str, k: int = 5) -> list[Document]:
        if not self._bm25 or not self._docs:
            return []
        scores = self._bm25.get_scores(query.lower().split())
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self._docs[i] for i in top_indices if scores[i] > 0]

    def is_ready(self) -> bool:
        return self._bm25 is not None


# Singleton instance
_bm25_index = BM25Index()


def get_bm25_index() -> BM25Index:
    return _bm25_index


async def build_bm25_from_chroma() -> None:
    """Fetch all docs from ChromaDB and build BM25 index."""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)
        result = collection.get(include=["documents", "metadatas"])

        docs = [
            Document(
                page_content=text,
                metadata=meta or {},
            )
            for text, meta in zip(result["documents"], result["metadatas"])
        ]
        _bm25_index.build(docs)
    except Exception as e:
        logger.error(f"Failed to build BM25 index: {e}")
