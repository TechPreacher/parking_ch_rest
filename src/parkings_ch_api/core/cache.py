"""Cache implementation for data sources."""

import time
from typing import Any, Dict, Generic, TypeVar

from ..config.settings import get_settings
from ..utils.logging import setup_logging

T = TypeVar("T")
logger = setup_logging(__name__)


class Cache(Generic[T]):
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize an empty cache."""
        self._cache: Dict[str, tuple[T, float]] = {}
        self._settings = get_settings()

    def get(self, key: str) -> T | None:
        """Get a value from the cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            T | None: Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._settings.cache_ttl:
            logger.debug(f"Cache entry expired for key: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit for key: {key}")
        return value

    def set(self, key: str, value: T) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        logger.debug(f"Caching value for key: {key}")
        self._cache[key] = (value, time.time())

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            logger.debug(f"Invalidating cache for key: {key}")
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        logger.debug("Clearing entire cache")
        self._cache.clear()
