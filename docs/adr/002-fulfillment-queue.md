# ADR-002: Fulfillment Queue Architecture

## Status

Accepted

## Date

2024-09-22

## Context

The order-service needs to hand off confirmed orders to the fulfillment-engine for processing. We need to decouple these two services to allow independent scaling and prevent order submission latency from being affected by fulfillment processing time.

## Decision

We use an SQS-based message queue between order-service and fulfillment-engine.

### Design

- **Producer**: order-service publishes `order.created` events after order confirmation.
- **Consumer**: fulfillment-engine polls the queue in configurable batches (default: 50 messages).
- **Visibility timeout**: 5 minutes (allows retry on processing failure).
- **Dead-letter queue**: Messages that fail 3 times are routed to a DLQ for manual investigation.

### Message Format

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

## Consequences

### Positive

- Order submission remains fast (publish-and-return).
- Fulfillment engine can scale independently based on queue depth.
- Built-in retry semantics via SQS visibility timeout.
- DLQ captures poison messages without blocking the pipeline.

### Negative

- Eventual consistency: order status updates are asynchronous.
- Additional infrastructure to monitor (queue depth, DLQ size).
- Message ordering not guaranteed (acceptable — orders are independent).
