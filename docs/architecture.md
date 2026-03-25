# ShelfLife Platform Architecture

## Overview

ShelfLife is a distributed e-commerce fulfillment platform built as a collection of microservices communicating via REST APIs and asynchronous message queues. The platform handles order intake, inventory management, warehouse operations, and customer notifications.

## Service Map

| Service | Port | Purpose |
|---------|------|---------|
| web-gateway | 8080 | Public API gateway, rate limiting, request routing |
| order-service | 8081 | Order lifecycle management, queue publishing |
| fulfillment-engine | 8082 | Batch order processing, stock allocation |
| warehouse-api | 8083 | Stock mutations (receive, pick, adjust) |
| notification-service | 8084 | Transactional email delivery |
| analytics-service | 8085 | Event ingestion and rollup |
| auth-service | 8086 | JWT tokens and API key management |
| scheduler-service | 8087 | Cron job orchestration |
| inventory-cache | 6379 | Redis — stock level caching |

## Data Flow

1. Requests enter through **web-gateway** which handles rate limiting and proxies to internal services.
2. **order-service** validates and persists orders, then publishes events to the fulfillment queue.
3. **fulfillment-engine** polls the queue in batches, checks stock levels via the cache, and coordinates picks with the warehouse API.
4. **warehouse-api** performs stock mutations against PostgreSQL and writes through to the inventory cache.
5. **notification-service** sends transactional emails (order confirmations, shipping updates) via SendGrid.

## Inventory Cache Strategy

The inventory cache uses a **write-through** pattern with a **TTL of 1 hour**. Every stock mutation performed by the warehouse-api writes the new quantity to both PostgreSQL and Redis simultaneously. Under normal traffic patterns, the frequent write-through operations from ongoing order fulfillment mean cache entries refresh well before TTL expiry.

If a cache miss occurs (e.g., for a rarely-accessed SKU), the fulfillment engine falls back to a direct database read and populates the cache on that read path.

### Cache Configuration

- Engine: Redis 7
- Eviction policy: `noeviction` (bounded keyspace — one entry per SKU)
- Max memory: 512MB (sufficient for ~2M SKU entries)
- TTL: 3600 seconds (1 hour)

## Infrastructure

- **Compute**: AWS ECS Fargate (Kubernetes manifests available for hybrid deployments)
- **Database**: Aurora PostgreSQL 15
- **Cache**: ElastiCache Redis 7 (multi-AZ, encryption at rest + in transit)
- **Queue**: SQS for fulfillment event processing
- **Observability**: Datadog APM + CloudWatch Logs

## Deployment

Services are deployed independently via CI/CD. Each service has its own Docker image pushed to ECR. The scheduler-service reads job definitions from a ConfigMap (Kubernetes) or mounted volume.
