# ADR-001: Inventory Cache Strategy

## Status

Accepted

## Date

2024-09-15

## Context

The fulfillment engine needs fast access to current stock levels when processing order batches. Direct database reads for every SKU check would create unacceptable latency at our target throughput of 500+ orders/minute.

We evaluated several caching strategies:

1. **Read-through with TTL** — Cache populated on read miss, expires after TTL.
2. **Write-through with TTL** — Cache updated on every write, with TTL as a safety net.
3. **Event-driven invalidation** — Cache invalidated via change-data-capture events.

## Decision

We chose **write-through caching with a 1-hour TTL**.

Every stock mutation (receive, pick, adjust) performed by the warehouse-api writes the updated quantity to both PostgreSQL and the Redis cache in the same operation. The TTL acts as a safety net rather than the primary freshness mechanism.

Under normal traffic patterns, the continuous flow of write-through operations from order fulfillment activity keeps cache entries fresh — entries are refreshed well before TTL expiry through natural write traffic.

### Configuration

- TTL: 3600 seconds (1 hour)
- Eviction policy: `noeviction`
- Max memory: 512MB
- Key format: `stock:{sku}`

## Consequences

### Positive

- Sub-millisecond stock reads for the fulfillment engine.
- Strong consistency during normal operations — writes update both stores atomically.
- Simple mental model: the cache always reflects the latest write.
- No additional infrastructure for change-data-capture.

### Negative

- If the cache write fails, the entry may serve stale data until TTL expiry or next successful write.
- Memory bounded by total SKU count (acceptable at current scale of ~500K SKUs).

### Risks

- If write traffic drops significantly for specific SKUs, their cache entries could reach TTL expiry and require a DB fallback read. This is acceptable — the fallback path repopulates the cache on read.
