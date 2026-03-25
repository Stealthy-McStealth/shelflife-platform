"""Batch writer for optimized stock mutations.

Groups individual stock updates into batched transactions for improved
database throughput during high-volume operations (receiving, cycle counts).
"""

import logging
from typing import List
from .config import settings
from .stock_manager import batch_update

logger = logging.getLogger(__name__)


class BatchWriter:
    def __init__(self, conn, batch_size: int | None = None):
        self._conn = conn
        self._batch_size = batch_size or settings.BATCH_SIZE
        self._buffer: List[dict] = []

    def add(self, sku: str, qty: int) -> None:
        """Add a mutation to the batch buffer."""
        self._buffer.append({"sku": sku, "qty": qty})
        if len(self._buffer) >= self._batch_size:
            self.flush()

    def flush(self) -> int:
        """Flush current buffer to database and cache."""
        if not self._buffer:
            return 0

        count = len(self._buffer)
        batch_update(self._conn, self._buffer)
        logger.info(f"batch_flush count={count}")
        self._buffer = []
        return count

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()
