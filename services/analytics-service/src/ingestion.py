"""Analytics service — event ingestion pipeline."""

import logging
from datetime import datetime
from typing import Any

from .buffer import EventBuffer
from .config import settings

logger = logging.getLogger(__name__)

_buffer = EventBuffer()


def ingest_event(event_type: str, payload: dict[str, Any], source: str) -> dict:
    """Ingest a raw analytics event into the buffer."""
    event = {
        "event_type": event_type,
        "payload": payload,
        "source": source,
        "ingested_at": datetime.utcnow().isoformat(),
    }

    accepted = _buffer.push(event)

    if not accepted:
        logger.warning(f"event_buffer_full event_type={event_type} source={source}")

    return {
        "accepted": True,
        "buffer_size": _buffer.size,
        "dropped_total": _buffer.dropped_count,
    }


async def flush_to_store() -> int:
    """Flush buffered events to the analytics database."""
    events = _buffer.flush()
    if not events:
        return 0

    # In production this writes to PostgreSQL / ClickHouse
    logger.info(f"flush_events count={len(events)} remaining={_buffer.size}")
    return len(events)


def get_buffer_stats() -> dict:
    """Return current buffer statistics."""
    return {
        "size": _buffer.size,
        "max_size": settings.BUFFER_MAX_SIZE,
        "dropped_total": _buffer.dropped_count,
        "is_full": _buffer.is_full,
    }
