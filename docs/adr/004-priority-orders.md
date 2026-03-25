# ADR-004: Priority Order Processing

## Status

Accepted

## Date

2024-10-18

## Context

Certain customers (enterprise accounts, same-day delivery) require their orders to be processed ahead of standard orders. The fulfillment engine processes orders in FIFO batches, which means high-priority orders could be delayed behind a large queue of standard orders.

## Decision

We introduced a priority flag on orders and a dual-queue processing strategy in the fulfillment engine.

### Design

- Orders with `priority: true` are published to a separate high-priority queue.
- The fulfillment engine polls the priority queue first on each processing cycle.
- If the priority queue is empty, it falls back to the standard queue.
- Priority orders skip the zero-stock check and instead reserve stock optimistically, triggering a backorder flow if stock is insufficient.

### Processing Logic

```
1. Poll priority queue (batch_size messages)
2. If priority batch is non-empty → process it
3. Else → poll standard queue (batch_size messages) → process
4. Sleep processing_interval_ms
5. Repeat
```

## Consequences

### Positive

- Priority orders are processed within seconds of submission regardless of standard queue depth.
- No starvation — standard orders still process when priority queue is empty (which is the common case).
- Backorder flow for priority orders prevents rejection when stock is tight.

### Negative

- Additional queue infrastructure to manage.
- Priority orders can consume stock that was expected by earlier standard orders (mitigated by backorder notifications).
- Potential for abuse if priority flag is not properly gated by business rules.
