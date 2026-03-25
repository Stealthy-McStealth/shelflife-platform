"""Analytics Service — FastAPI application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .config import settings
from .ingestion import ingest_event, flush_to_store, get_buffer_stats

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("analytics-service starting")
    task = asyncio.create_task(_flush_loop())
    yield
    task.cancel()


app = FastAPI(title="analytics-service", lifespan=lifespan)


class AnalyticsEvent(BaseModel):
    event_type: str
    payload: dict
    source: str


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "analytics-service"}


@app.post("/api/events", status_code=202)
async def record_event(event: AnalyticsEvent):
    """Ingest an analytics event."""
    result = ingest_event(event.event_type, event.payload, event.source)
    return result


@app.get("/api/events/stats")
async def buffer_stats():
    """Return current buffer statistics."""
    return get_buffer_stats()


@app.post("/api/events/flush")
async def manual_flush():
    """Manually trigger a buffer flush."""
    count = await flush_to_store()
    return {"flushed": count}


async def _flush_loop():
    """Periodic flush of buffered events to persistent store."""
    while True:
        try:
            await asyncio.sleep(settings.FLUSH_INTERVAL_SECONDS)
            count = await flush_to_store()
            if count > 0:
                logger.info(f"periodic_flush count={count}")
        except asyncio.CancelledError:
            # Final flush on shutdown
            await flush_to_store()
            break
        except Exception as e:
            logger.error(f"flush_loop_error error={e}")
