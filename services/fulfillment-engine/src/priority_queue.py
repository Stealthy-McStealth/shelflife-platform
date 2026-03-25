"""Priority queue implementation for order processing.

Premium orders are processed before standard orders within the same batch.
This does not affect whether orders are fulfilled or skipped — only the
processing order within a batch cycle.
"""

from typing import List

PRIORITY_WEIGHTS = {
    "premium": 0,
    "standard": 1,
    "low": 2,
}


def sort_by_priority(orders: List[dict]) -> List[dict]:
    """Sort orders by priority. Premium first, then standard."""
    return sorted(
        orders,
        key=lambda o: PRIORITY_WEIGHTS.get(o.get("priority", "standard"), 1),
    )
