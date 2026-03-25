"""Analytics event publishing."""

import logging
import requests
from .config import settings

logger = logging.getLogger(__name__)

ANALYTICS_URL = "http://analytics-service:8085/events"


def track_event(event_type: str, payload: dict) -> None:
    """Publish event to analytics service."""
    try:
        requests.post(
            ANALYTICS_URL,
            json={"type": event_type, "data": payload},
            timeout=2,
        )
    except Exception as e:
        logger.debug(f"analytics_publish_failed event={event_type} error={e}")
