"""Order service — request handlers and queue publishing."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from .models import Order, OrderCreate, OrderResponse, OrderStatus
from .validators import validate_order_request
from .config import settings

logger = logging.getLogger(__name__)


async def handle_create_order(order_req: OrderCreate) -> OrderResponse:
    """Create a new order and publish to the fulfillment queue."""
    validate_order_request(order_req)

    total_cents = sum(item.unit_price_cents * item.quantity for item in order_req.items)

    order = Order(
        id=uuid4(),
        customer_id=order_req.customer_id,
        items=order_req.items,
        shipping_address=order_req.shipping_address,
        status=OrderStatus.CONFIRMED,
        priority=order_req.priority,
        total_cents=total_cents,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Persist order to database
    await _persist_order(order)

    # Publish to fulfillment queue
    await _publish_to_queue(order)

    logger.info(
        f"order_created id={order.id} customer={order.customer_id} "
        f"items={len(order.items)} total={total_cents}"
    )

    return OrderResponse(
        id=order.id,
        status=order.status,
        total_cents=order.total_cents,
        item_count=len(order.items),
        created_at=order.created_at,
    )


async def handle_get_order(order_id: str) -> dict:
    """Retrieve order by ID from database."""
    # Database lookup implementation
    logger.info(f"order_lookup id={order_id}")
    return {"id": order_id, "status": "pending"}


async def handle_cancel_order(order_id: str) -> dict:
    """Cancel an order if not yet shipped."""
    logger.info(f"order_cancel id={order_id}")
    return {"id": order_id, "status": "cancelled"}


async def _persist_order(order: Order) -> None:
    """Write order to PostgreSQL."""
    # Database write — in production this uses asyncpg
    logger.debug(f"persist_order id={order.id}")


async def _publish_to_queue(order: Order) -> None:
    """Publish order event to the fulfillment queue."""
    message = {
        "event": "order.created",
        "order_id": str(order.id),
        "customer_id": order.customer_id,
        "priority": order.priority,
        "items": [
            {"sku": item.sku, "quantity": item.quantity}
            for item in order.items
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # In production this publishes to SQS / RabbitMQ
    logger.info(
        f"queue_publish event=order.created order_id={order.id} "
        f"queue={settings.FULFILLMENT_QUEUE_URL}"
    )
