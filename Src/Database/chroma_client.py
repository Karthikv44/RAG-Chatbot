"""
Singleton ChromaDB client.
Local: persistent file-based client (no server needed).
Production: swap to AsyncHttpClient pointing at a hosted ChromaDB instance.
"""
from functools import lru_cache
import chromadb
from Src.Config.config import get_settings

settings = get_settings()

COLLECTION_NAME = "rag_documents"
CHROMA_PERSIST_DIR = "./data/chroma"


@lru_cache
def get_chroma_client() -> chromadb.PersistentClient:
    """Singleton persistent ChromaDB client (local file-based)."""
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


async def get_or_create_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
