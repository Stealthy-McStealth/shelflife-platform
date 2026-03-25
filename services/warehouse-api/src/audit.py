"""Stock adjustment audit logging."""

import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ANALYTICS_URL = "http://analytics-service:8085/events"


def log_adjustment(sku: str, old_qty: int, new_qty: int, reason: str, user: str) -> None:
    """Emit audit event for stock adjustment."""
    event = {
        "type": "stock_adjustment",
        "data": {
            "sku": sku,
            "old_qty": old_qty,
            "new_qty": new_qty,
            "delta": new_qty - old_qty,
            "reason": reason,
            "user": user,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    try:
        requests.post(ANALYTICS_URL, json=event, timeout=2)
    except Exception as e:
        logger.warning(f"audit_publish_failed sku={sku} error={e}")
