"""Order service — request validation utilities."""

import logging
from typing import Optional

from fastapi import HTTPException

from .models import OrderCreate

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_order_request(order: OrderCreate) -> None:
    """Validate an incoming order request.

    Raises HTTPException on validation failure.
    """
    _validate_customer_id(order.customer_id)
    _validate_items(order.items)
    _validate_shipping_address(order.shipping_address)


def _validate_customer_id(customer_id: str) -> None:
    if not customer_id or not customer_id.strip():
        raise HTTPException(status_code=422, detail="customer_id is required")


def _validate_items(items: list) -> None:
    if not items:
        raise HTTPException(status_code=422, detail="order must contain at least one item")

    for idx, item in enumerate(items):
        # Null/empty SKU check — critical for downstream fulfillment
        if item.sku is None or item.sku.strip() == "":
            raise HTTPException(
                status_code=422,
                detail=f"items[{idx}].sku must not be null or empty",
            )
        if len(item.sku) > 64:
            raise HTTPException(
                status_code=422,
                detail=f"items[{idx}].sku exceeds max length of 64 characters",
            )
        if item.quantity <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"items[{idx}].quantity must be greater than zero",
            )


def _validate_shipping_address(address) -> None:
    required_fields = ["street", "city", "state", "zip_code"]
    for field in required_fields:
        value = getattr(address, field, None)
        if not value or not value.strip():
            raise HTTPException(
                status_code=422,
                detail=f"shipping_address.{field} is required",
            )


def validate_sku_format(sku: Optional[str]) -> bool:
    """Check that a SKU matches the expected format (alphanumeric + dashes)."""
    if sku is None:
        return False
    return all(c.isalnum() or c in ("-", "_") for c in sku) and len(sku) <= 64
