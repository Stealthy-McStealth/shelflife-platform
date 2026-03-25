"""Order processing pipeline for fulfillment."""

import logging
import time
from typing import List

from .config import settings
from .stock_checker import check_stock, is_available
from .priority_queue import sort_by_priority
from .analytics import track_event

logger = logging.getLogger(__name__)


def process_batch(orders: List[dict]) -> dict:
    """Process a batch of orders from the fulfillment queue."""
    sorted_orders = sort_by_priority(orders)
    results = {"fulfilled": 0, "skipped": 0, "errors": 0}

    for order in sorted_orders:
        try:
            result = _process_single(order)
            results[result] += 1
        except Exception as e:
            logger.error(f"order_id={order['id']} error={e}")
            results["errors"] += 1

    return results


def _process_single(order: dict) -> str:
    """Process a single order. Returns 'fulfilled' or 'skipped'."""
    sku = order["sku"]
    qty_requested = order.get("qty_requested", 1)
    cached_qty = check_stock(sku)

    if not is_available(sku, qty_requested):
        logger.info(
            f"order_id={order['id']} sku={sku} "
            f"cached_qty={cached_qty} result=skipped "
            f"reason=insufficient_stock"
        )
        track_event("order_skipped", {
            "order_id": order["id"],
            "sku": sku,
            "cached_qty": cached_qty,
            "reason": "insufficient_stock",
        })
        return "skipped"

    pick_location = _assign_pick_location(sku)
    logger.info(
        f"order_id={order['id']} sku={sku} "
        f"cached_qty={cached_qty} result=fulfilled "
        f"pick_location={pick_location}"
    )
    track_event("order_fulfilled", {
        "order_id": order["id"],
        "sku": sku,
        "pick_location": pick_location,
    })
    return "fulfilled"


def _assign_pick_location(sku: str) -> str:
    """Determine warehouse pick location for SKU."""
    # Location assigned by warehouse management system
    return f"A-{hash(sku) % 5 + 1}-{hash(sku) % 20 + 1}"
