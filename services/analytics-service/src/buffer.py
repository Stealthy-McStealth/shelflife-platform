"""Analytics service — bounded event buffer."""

import logging
import threading
from collections import deque
from typing import Any

from .config import settings

logger = logging.getLogger(__name__)


class EventBuffer:
    """Thread-safe bounded buffer for analytics events.

    When the buffer reaches max capacity, oldest events are dropped
    to prevent unbounded memory growth.
    """

    def __init__(self, max_size: int | None = None):
        self._max_size = max_size or settings.BUFFER_MAX_SIZE
        self._buffer: deque[dict[str, Any]] = deque(maxlen=self._max_size)
        self._lock = threading.Lock()
        self._dropped_count = 0

    def push(self, event: dict[str, Any]) -> bool:
        """Add an event to the buffer. Returns False if buffer was full (oldest dropped)."""
        with self._lock:
            was_full = len(self._buffer) >= self._max_size
            self._buffer.append(event)
            if was_full:
                self._dropped_count += 1
                logger.warning(
                    f"buffer_overflow dropped_total={self._dropped_count} "
                    f"max_size={self._max_size}"
                )
            return not was_full

    def flush(self, batch_size: int | None = None) -> list[dict[str, Any]]:
        """Drain up to batch_size events from the buffer."""
        size = batch_size or settings.FLUSH_BATCH_SIZE
        with self._lock:
            events = []
            for _ in range(min(size, len(self._buffer))):
                events.append(self._buffer.popleft())
            return events

    @property
    def size(self) -> int:
        return len(self._buffer)

    @property
    def dropped_count(self) -> int:
        return self._dropped_count

    @property
    def is_full(self) -> bool:
        return len(self._buffer) >= self._max_size
