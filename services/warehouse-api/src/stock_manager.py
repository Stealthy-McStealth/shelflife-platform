"""Stock mutation manager with write-through cache."""

import logging
from typing import List

from .config import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency at module level
_cache_client = None


def _get_cache():
    global _cache_client
    if _cache_client is None:
        from inventory_cache.client import InventoryCacheClient
        _cache_client = InventoryCacheClient(redis_url=settings.REDIS_URL)
    return _cache_client


def update_stock(conn, sku: str, new_qty: int) -> None:
    """Update stock in DB and write-through to cache."""
    conn.execute(
        "UPDATE inventory SET qty = %s, updated_at = NOW() WHERE sku = %s",
        (new_qty, sku),
    )
    conn.commit()
    _get_cache().set_stock(sku, new_qty)
    logger.info(f"mutation=stock_update sku={sku} qty={new_qty} cache_write=success")


def batch_update(conn, mutations: List[dict]) -> None:
    """Batch stock updates for throughput.

    Groups mutations into a single DB transaction while maintaining
    per-item cache writes for consistency.
    """
    for m in mutations:
        conn.execute(
            "UPDATE inventory SET qty = %s, updated_at = NOW() WHERE sku = %s",
            (m["qty"], m["sku"]),
        )
    conn.commit()

    for m in mutations:
        _get_cache().set_stock(m["sku"], m["qty"])
        logger.info(
            f"mutation=stock_update sku={m['sku']} qty={m['qty']} cache_write=success"
        )
