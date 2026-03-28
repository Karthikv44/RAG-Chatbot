"""
Vector store repository — wraps ChromaDB operations.
Strategy pattern: interface allows swapping vector stores later.
"""
from typing import Protocol
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
from Src.Database.chroma_client import COLLECTION_NAME, get_chroma_client
from Src.Config.config import get_settings

settings = get_settings()


class VectorStoreStrategy(Protocol):
    async def add_documents(self, documents: list[Document]) -> int: ...
    async def similarity_search(self, query: str, k: int = 5) -> list[Document]: ...


class ChromaVectorRepository:
    """Concrete strategy using ChromaDB persistent client + Bedrock Titan embeddings."""

    def __init__(self, embeddings: BedrockEmbeddings):
        self._embeddings = embeddings
        self._store: Chroma | None = None

    def _get_store(self) -> Chroma:
        if self._store is None:
            client = get_chroma_client()
            self._store = Chroma(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding_function=self._embeddings,
            )
        return self._store

    async def add_documents(self, documents: list[Document]) -> int:
        store = self._get_store()
        await store.aadd_documents(documents)
        return len(documents)

    async def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        store = self._get_store()
        return await store.asimilarity_search(query, k=k)
