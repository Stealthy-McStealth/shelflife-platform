# Runbook: Inventory Cache Operations

## Service Overview

The inventory cache is a Redis 7 instance that holds current stock levels for all active SKUs. It uses a write-through pattern: every stock mutation updates both PostgreSQL and Redis. TTL is set to 1 hour as a safety net.

## Health Checks

```bash
# Ping Redis
redis-cli -h $REDIS_HOST ping

# Check memory usage
redis-cli -h $REDIS_HOST info memory

# Check connected clients
redis-cli -h $REDIS_HOST info clients

# Check keyspace stats
redis-cli -h $REDIS_HOST info keyspace
```

## Common Operations

### Check Stock for a SKU

```bash
redis-cli -h $REDIS_HOST get "stock:SKU-12345"
redis-cli -h $REDIS_HOST ttl "stock:SKU-12345"
```

### Manually Invalidate a Cache Entry

Use this only if you have confirmed a stale entry that has not yet self-healed:

```bash
redis-cli -h $REDIS_HOST del "stock:SKU-12345"
```

The next read from the fulfillment engine will trigger a DB fallback and repopulate the cache.

### Bulk Key Inspection

```bash
# Count total stock keys
redis-cli -h $REDIS_HOST eval "return #redis.call('keys', 'stock:*')" 0

# Find keys with low TTL (< 60 seconds)
redis-cli -h $REDIS_HOST --scan --pattern "stock:*" | while read key; do
  ttl=$(redis-cli -h $REDIS_HOST ttl "$key")
  if [ "$ttl" -lt 60 ] && [ "$ttl" -gt 0 ]; then
    echo "$key TTL=$ttl"
  fi
done
```

## Troubleshooting

### Cache Miss Rate Increasing

**Possible causes**:
- Normal: traffic pattern shifted to include rarely-accessed SKUs. The read-fallback path will repopulate.
- Write-through failures: check warehouse-api logs for Redis connection errors.

**Investigation**:
```bash
# Check Redis connection errors in warehouse-api
kubectl logs -l app=warehouse-api -n shelflife | grep "redis" | grep -i "error"

# Check Redis maxmemory status
redis-cli -h $REDIS_HOST info memory | grep "used_memory_human\|maxmemory_human"
```

### Redis Memory Near Limit

```bash
# Check current usage vs max
redis-cli -h $REDIS_HOST info memory | grep maxmemory

# Count keys
redis-cli -h $REDIS_HOST dbsize
```

The eviction policy is `noeviction`, meaning Redis will reject writes if memory is exhausted. If approaching the limit, consider increasing the `maxmemory` configuration.

### Connectivity Issues

```bash
# Test from a service pod
kubectl exec -it deploy/fulfillment-engine -n shelflife -- python -c "
import redis
r = redis.Redis.from_url('$REDIS_URL')
print(r.ping())
"

# Check ElastiCache node status (AWS)
aws elasticache describe-replication-groups \
  --replication-group-id shelflife-inventory-cache-production
```

## Configuration Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| maxmemory | 512mb | Maximum memory allocation |
| maxmemory-policy | noeviction | Reject writes when full |
| Default TTL | 3600s | Applied to all stock entries |
| Key format | `stock:{sku}` | One key per SKU |

## Escalation

For persistent Redis issues, escalate to `#platform-eng` with Redis INFO output and relevant service logs.
