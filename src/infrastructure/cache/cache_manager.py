"""In-memory cache manager with TTL support and RedisCache contract."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any


class MemoryCache:
    """In-memory key-value cache with TTL expiration support."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, datetime | None]] = {}

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store key-value pair with optional TTL."""
        expiry = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds else None
        self._store[key] = (value, expiry)

    def get(self, key: str) -> Any | None:
        """Retrieve value by key if not expired."""
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if expiry and datetime.now(UTC) > expiry:
            del self._store[key]
            return None
        return val

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()


class RedisCache(ABC):
    """Abstract Redis cache interface contract."""

    @abstractmethod
    async def get_async(self, key: str) -> str | None:
        """Retrieve cached string asynchronously."""
        pass

    @abstractmethod
    async def set_async(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """Set cached string asynchronously."""
        pass


class CacheManager:
    """Cache manager providing memory cache instances."""

    def __init__(self) -> None:
        self.memory_cache = MemoryCache()
