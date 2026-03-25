# Warehouse API Reference

**Base URL**: `http://warehouse-api:8083`

## Endpoints

### Health Check

```
GET /health
```

**Response** `200 OK`:
```json
{"status": "healthy", "service": "warehouse-api"}
```

---

### Receive Stock

Record goods receipt into inventory.

```
POST /api/stock/receive
```

**Request Body**:
```json
{
  "sku": "SKU-12345",
  "qty": 100,
  "reason": "PO-2024-001 received"
}
```

**Response** `200 OK`:
```json
{"status": "accepted", "sku": "SKU-12345"}
```

---

### Pick Stock

Record a pick operation (decrement stock for an order).

```
POST /api/stock/pick
```

**Request Body**:
```json
{
  "sku": "SKU-12345",
  "qty": 2,
  "reason": "order-abc123"
}
```

**Response** `200 OK`:
```json
{"status": "accepted", "sku": "SKU-12345"}
```

---

### Adjust Stock

Manual inventory adjustment (cycle count correction, damage write-off, etc.).

```
POST /api/stock/adjust
```

**Request Body**:
```json
{
  "sku": "SKU-12345",
  "qty": -5,
  "reason": "damaged in transit"
}
```

**Response** `200 OK`:
```json
{"status": "accepted", "sku": "SKU-12345"}
```

---

### Batch Mutations

Submit multiple stock mutations in a single atomic operation.

```
POST /api/stock/batch
```

**Request Body**:
```json
{
  "mutations": [
    {"sku": "SKU-001", "qty": -1, "reason": "order-pick"},
    {"sku": "SKU-002", "qty": -2, "reason": "order-pick"},
    {"sku": "SKU-003", "qty": 50, "reason": "restock"}
  ]
}
```

**Response** `200 OK`:
```json
{"status": "accepted", "count": 3}
```

**Constraints**:
- Maximum 50 mutations per batch.
- All mutations are applied atomically.

---

### Get Stock Level

Retrieve current stock quantity for a SKU.

```
GET /api/stock/{sku}
```

**Response** `200 OK`:
```json
{"sku": "SKU-12345", "qty": 95, "source": "warehouse-db"}
```

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body |
| 404 | SKU not found |
| 422 | Validation error (e.g., negative qty on receive) |
| 500 | Internal server error |

## Notes

- All mutations write through to the inventory cache (Redis) after the database transaction commits.
- The `qty` field is a delta for receive/adjust and an absolute pick count for pick operations.
- The `reason` field is optional but recommended for audit trail purposes.
