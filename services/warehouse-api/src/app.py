"""Warehouse API — stock mutation service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("warehouse-api starting")
    yield


app = FastAPI(title="warehouse-api", lifespan=lifespan)


class StockMutation(BaseModel):
    sku: str
    qty: int
    reason: str | None = None


class BatchMutation(BaseModel):
    mutations: list[StockMutation]


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "warehouse-api"}


@app.post("/api/stock/receive")
async def receive_stock(mutation: StockMutation):
    """Record goods receipt."""
    logger.info(f"mutation=receive sku={mutation.sku} qty={mutation.qty}")
    return {"status": "accepted", "sku": mutation.sku}


@app.post("/api/stock/pick")
async def pick_stock(mutation: StockMutation):
    """Record order pick."""
    logger.info(f"mutation=pick sku={mutation.sku} qty={mutation.qty}")
    return {"status": "accepted", "sku": mutation.sku}


@app.post("/api/stock/adjust")
async def adjust_stock(mutation: StockMutation):
    """Manual inventory adjustment."""
    logger.info(f"mutation=adjust sku={mutation.sku} qty={mutation.qty} reason={mutation.reason}")
    return {"status": "accepted", "sku": mutation.sku}


@app.post("/api/stock/batch")
async def batch_mutations(batch: BatchMutation):
    """Batch stock mutations for throughput."""
    logger.info(f"batch_mutation count={len(batch.mutations)}")
    return {"status": "accepted", "count": len(batch.mutations)}


@app.get("/api/stock/{sku}")
async def get_stock(sku: str):
    """Get current stock quantity from DB."""
    return {"sku": sku, "qty": 0, "source": "warehouse-db"}
