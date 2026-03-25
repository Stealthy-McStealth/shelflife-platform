# New Hire Onboarding Guide

Welcome to the ShelfLife platform team! This guide will help you get your local development environment set up.

## Prerequisites

- Docker Desktop (v4.25+)
- Python 3.11+
- Node.js 20+ (for frontend tooling)
- AWS CLI v2 (configured with `shelflife-dev` profile)
- `make` (build orchestration)

## Initial Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:shelflife/platform.git
   cd platform
   ```

2. Run the setup script:
   ```bash
   ./setup-repo.sh
   ```

3. Start all services locally:
   ```bash
   make up
   ```

4. Verify everything is healthy:
   ```bash
   make health
   ```

5. Seed the local database with test data:
   ```bash
   make seed
   ```

## Local Development

### Running a Single Service

```bash
# Start just the order-service with hot reload
cd services/order-service
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8081
```

### Running Tests

```bash
make test                    # All tests
make test-service SVC=order-service  # Single service
```

### Viewing Logs

```bash
docker compose logs -f order-service
docker compose logs -f fulfillment-engine
```

## Key Concepts

- **Write-through cache**: Stock mutations write to both DB and Redis. Under normal traffic patterns, entries refresh before TTL expiry.
- **Batch processing**: The fulfillment engine processes orders in configurable batches (default 50) for throughput.
- **Priority queue**: Orders flagged as priority are processed before standard orders.

## Service Ports (Local)

| Service | Port |
|---------|------|
| web-gateway | 8080 |
| order-service | 8081 |
| fulfillment-engine | 8082 |
| warehouse-api | 8083 |
| notification-service | 8084 |
| analytics-service | 8085 |
| auth-service | 8086 |
| scheduler-service | 8087 |
| inventory-cache (Redis) | 6379 |
| PostgreSQL | 5432 |

## Useful Commands

```bash
make up          # Start all services
make down        # Stop all services
make logs        # Tail all logs
make test        # Run test suite
make lint        # Run linters
make build       # Build all Docker images
make seed        # Seed local database
make health      # Check service health
```

## Getting Help

- Platform architecture: `docs/architecture.md`
- ADRs: `docs/adr/`
- Runbooks: `docs/runbooks/`
- Slack: `#platform-eng`
