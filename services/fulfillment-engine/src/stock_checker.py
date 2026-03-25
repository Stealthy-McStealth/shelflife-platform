"""Stock availability checker using inventory cache."""

import redis

from .config import settings

_cache = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def check_stock(sku: str) -> int:
    """Return cached quantity for SKU. Returns 0 if key missing/expired."""
    val = _cache.get(f"stock:{sku}")
    if val is None:
        return 0
    return int(val)


def is_available(sku: str, requested_qty: int) -> bool:
    """Check if requested quantity is available in cache."""
    cached = check_stock(sku)
    if settings.SKIP_ZERO_STOCK and cached == 0:
        return False
    return cached >= requested_qty
