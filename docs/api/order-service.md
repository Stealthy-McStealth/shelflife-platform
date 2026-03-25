# Order Service API Reference

**Base URL**: `http://order-service:8081`

## Endpoints

### Health Check

```
GET /health
```

**Response** `200 OK`:
```json
{"status": "healthy", "service": "order-service"}
```

---

### Create Order

Submit a new order for fulfillment.

```
POST /api/orders
```

**Request Body**:
```json
{
  "customer_id": "cust-abc123",
  "items": [
    {
      "sku": "SKU-12345",
      "quantity": 2,
      "unit_price_cents": 1499,
      "name": "Widget Pro"
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "Portland",
    "state": "OR",
    "zip_code": "97201",
    "country": "US"
  },
  "priority": false
}
```

**Response** `201 Created`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "confirmed",
  "total_cents": 2998,
  "item_count": 1,
  "created_at": "2024-10-15T14:30:00Z"
}
```

---

### Get Order

Retrieve an order by ID.

```
GET /api/orders/{order_id}
```

**Response** `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

---

### Cancel Order

Cancel a pending or confirmed order. Orders that have already shipped cannot be cancelled.

```
POST /api/orders/{order_id}/cancel
```

**Response** `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled"
}
```

---

### List Orders

List orders with optional filtering.

```
GET /api/orders?customer_id=cust-abc123&limit=50&offset=0
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| customer_id | string | null | Filter by customer |
| limit | int | 50 | Page size (max 100) |
| offset | int | 0 | Pagination offset |

**Response** `200 OK`:
```json
{
  "orders": [],
  "total": 0
}
```

## Validation Rules

- `customer_id` must be non-empty.
- `items` must contain at least one item.
- Each item's `sku` must not be null or empty (max 64 characters).
- Each item's `quantity` must be greater than zero.
- Shipping address fields (`street`, `city`, `state`, `zip_code`) are all required.

## Error Responses

| Status | Meaning |
|--------|---------|
| 404 | Order not found |
| 422 | Validation error |
| 500 | Internal server error |

## Events Published

On successful order creation, the service publishes an `order.created` event to the fulfillment queue:

```json
{
  "event": "order.created",
  "order_id": "uuid",
  "customer_id": "string",
  "priority": false,
  "items": [{"sku": "string", "quantity": 1}],
  "timestamp": "ISO-8601"
}
```
