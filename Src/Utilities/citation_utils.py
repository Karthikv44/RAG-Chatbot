"""Formats retrieval results into citation metadata."""
from typing import Any


def format_citations(documents: list[Any]) -> list[dict]:
    """
    Extracts citation info from LangChain Document objects.
    Returns a list of {source, page} dicts.
    """
    seen = set()
    citations = []
    for doc in documents:
        meta = doc.metadata or {}
        source = meta.get("source", "unknown")
        page = meta.get("page", None)
        key = f"{source}:{page}"
        if key not in seen:
            seen.add(key)
            citations.append({"source": source, "page": page})
    return citations
