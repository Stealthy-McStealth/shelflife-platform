"""Redis cache client for inventory stock levels."""

import logging
import redis

from .config import settings

logger = logging.getLogger(__name__)


class InventoryCacheClient:
    def __init__(self, redis_url: str | None = None, ttl: int | None = None):
        self._redis = redis.Redis.from_url(
            redis_url or settings.REDIS_URL,
            decode_responses=True,
        )
        self._ttl = ttl or settings.DEFAULT_TTL

    def set_stock(self, sku: str, qty: int) -> None:
        """Set stock quantity with TTL."""
        self._redis.setex(f"stock:{sku}", self._ttl, str(qty))

    def get_stock(self, sku: str) -> int | None:
        """Get cached stock quantity. Returns None if expired/missing."""
        val = self._redis.get(f"stock:{sku}")
        return int(val) if val is not None else None

    def delete(self, sku: str) -> None:
        """Remove a stock entry from cache."""
        self._redis.delete(f"stock:{sku}")

    def ping(self) -> bool:
        """Check Redis connectivity."""
        try:
            return self._redis.ping()
        except redis.ConnectionError:
            return False
