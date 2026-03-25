# ADR-003: Batch Stock Mutations

## Status

Accepted

## Date

2024-10-05

## Context

During peak fulfillment periods, the warehouse-api receives hundreds of individual stock pick operations per second. Each pick requires a database write and a cache update. Individual operations create excessive connection overhead and limit throughput.

## Decision

We introduced a batch mutation endpoint (`POST /api/stock/batch`) that accepts up to 50 mutations in a single request. Mutations within a batch are applied in a single database transaction.

### Design

- Maximum batch size: 50 mutations (configurable via `BATCH_SIZE` env var).
- All mutations in a batch are applied atomically — either all succeed or all fail.
- Cache writes are performed after the transaction commits, one key at a time.
- If a cache write fails for an individual SKU, the error is logged but does not roll back the transaction.

### Batch Request Format

```json
{
  "mutations": [
    {"sku": "SKU-001", "qty": -1, "reason": "order-pick"},
    {"sku": "SKU-002", "qty": -2, "reason": "order-pick"}
  ]
}
```

## Consequences

### Positive

- 5-8x throughput improvement during batch processing compared to individual mutations.
- Reduced database connection usage.
- Atomic semantics ensure inventory consistency within a batch.

### Negative

- Larger blast radius on failure (entire batch fails if one mutation violates constraints).
- Slightly more complex error handling on the client side.
- Cache writes are not transactional with the DB write (acceptable given write-through pattern and TTL safety net).
