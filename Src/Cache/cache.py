"""
In-memory TTL + LRU cache for repeated RAG queries.
Avoids redundant Bedrock calls for identical questions.
"""
from cachetools import TTLCache, LRUCache
import hashlib
import json

# TTL cache: entries expire after 10 minutes
_ttl_cache: TTLCache = TTLCache(maxsize=256, ttl=600)

# LRU cache: keeps 128 most recently used entries
_lru_cache: LRUCache = LRUCache(maxsize=128)


def _make_key(query: str, user_id: str) -> str:
    raw = json.dumps({"query": query, "user_id": user_id}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(query: str, user_id: str) -> dict | None:
    key = _make_key(query, user_id)
    return _ttl_cache.get(key) or _lru_cache.get(key)


def set_cached_response(query: str, user_id: str, response: dict) -> None:
    key = _make_key(query, user_id)
    _ttl_cache[key] = response
    _lru_cache[key] = response


def invalidate_cache(query: str, user_id: str) -> None:
    key = _make_key(query, user_id)
    _ttl_cache.pop(key, None)
    _lru_cache.pop(key, None)
