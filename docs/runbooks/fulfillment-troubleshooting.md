# Runbook: Fulfillment Engine Troubleshooting

## Service Overview

The fulfillment-engine processes orders from the fulfillment queue in batches, validates stock availability via the inventory cache, and coordinates picks with the warehouse-api.

## Common Issues

### 1. Orders Stuck in "Processing" State

**Symptoms**: Orders remain in `processing` status for more than 5 minutes.

**Investigation**:
```bash
# Check fulfillment-engine logs
kubectl logs -l app=fulfillment-engine --tail=200 -n shelflife

# Check queue depth
aws sqs get-queue-attributes --queue-url $FULFILLMENT_QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages

# Check DLQ for poison messages
aws sqs get-queue-attributes --queue-url $FULFILLMENT_DLQ_URL \
  --attribute-names ApproximateNumberOfMessages
```

**Resolution**:
- If queue depth is growing: check if fulfillment-engine pods are healthy and processing.
- If DLQ has messages: inspect them for malformed order data (common: null SKU fields).
- If cache is returning misses: verify Redis connectivity (see cache-operations runbook).

### 2. Stock Allocation Failures

**Symptoms**: Orders fail with "insufficient stock" despite warehouse showing available inventory.

**Investigation**:
```bash
# Check cached stock level
redis-cli -h $REDIS_HOST get "stock:$SKU"

# Check actual DB stock level
psql $WAREHOUSE_DB -c "SELECT qty FROM stock_levels WHERE sku = '$SKU';"

# Compare values
```

**Resolution**:
- If cache shows lower value than DB: a cache write may have failed. The entry will self-heal at TTL expiry or on the next write-through operation.
- If both are low: check recent pick history for unexpected large orders.

### 3. High Processing Latency

**Symptoms**: `processing_loop` duration exceeds 2 seconds per batch.

**Investigation**:
```bash
# Check batch size configuration
kubectl get deployment fulfillment-engine -n shelflife -o jsonpath='{.spec.template.spec.containers[0].env}'

# Check Redis latency
redis-cli -h $REDIS_HOST --latency

# Check warehouse-api response times
kubectl logs -l app=warehouse-api --tail=100 -n shelflife | grep "elapsed_ms"
```

**Resolution**:
- Reduce `QUEUE_BATCH_SIZE` to decrease per-loop processing time.
- Scale warehouse-api if it is the bottleneck.
- Check if Redis is under memory pressure.

### 4. Fulfillment Engine Not Starting

**Symptoms**: Pod in CrashLoopBackOff.

**Investigation**:
```bash
kubectl describe pod -l app=fulfillment-engine -n shelflife
kubectl logs -l app=fulfillment-engine --previous -n shelflife
```

**Resolution**:
- Check for missing environment variables (REDIS_URL, FULFILLMENT_QUEUE_URL).
- Verify Redis and queue connectivity from the pod's network.

## Escalation

If the above steps do not resolve the issue, escalate to `#platform-eng` with:
- Timestamp of first observed failure
- Current queue depth
- Pod logs from the relevant timeframe
- Any recent deployments
