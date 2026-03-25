"""Order service — Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(gt=0)
    name: str


class ShippingAddress(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderItem] = Field(min_length=1)
    shipping_address: ShippingAddress
    priority: bool = False
    idempotency_key: Optional[str] = None


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer_id: str
    items: list[OrderItem]
    shipping_address: ShippingAddress
    status: OrderStatus = OrderStatus.PENDING
    priority: bool = False
    total_cents: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    total_cents: int
    item_count: int
    created_at: datetime
