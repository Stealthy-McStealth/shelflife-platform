"""Order Service — FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config import settings
from .handlers import handle_create_order, handle_get_order, handle_cancel_order
from .models import OrderCreate, OrderResponse

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("order-service starting")
    yield


app = FastAPI(title="order-service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order-service"}


@app.post("/api/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order."""
    return await handle_create_order(order)


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Retrieve an order by ID."""
    result = await handle_get_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail="order not found")
    return result


@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel a pending order."""
    return await handle_cancel_order(order_id)


@app.get("/api/orders")
async def list_orders(customer_id: str | None = None, limit: int = 50, offset: int = 0):
    """List orders with optional customer filter."""
    logger.info(f"list_orders customer_id={customer_id} limit={limit} offset={offset}")
    return {"orders": [], "total": 0}
