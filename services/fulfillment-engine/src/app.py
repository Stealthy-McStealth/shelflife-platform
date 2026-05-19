"""Fulfillment Engine — FastAPI application."""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .order_processor import process_batch

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("fulfillment-engine starting")
    task = asyncio.create_task(_processing_loop())
    yield
    task.cancel()


app = FastAPI(title="fulfillment-engine", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fulfillment-engine"}


@app.get("/metrics")
async def metrics():
    return {
        "queue_batch_size": settings.QUEUE_BATCH_SIZE,
        "processing_interval_ms": settings.PROCESSING_INTERVAL_MS,
        "skip_zero_stock": settings.SKIP_ZERO_STOCK,
    }


async def _processing_loop():
    """Main processing loop — polls queue and processes batches."""
    while True:
        try:
            orders = await _poll_queue(settings.QUEUE_BATCH_SIZE)
            if orders:
                process_batch(orders)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"processing_loop_error error={e}")

        await asyncio.sleep(settings.PROCESSING_INTERVAL_MS / 1000)


async def _poll_queue(batch_size: int) -> list:
    """Poll fulfillment queue for pending orders."""
    # Queue polling implementation (SQS / internal queue)
    return []

# Datadog APM integration for distributed tracing

