# ShelfLife Platform

Distributed e-commerce fulfillment platform powering order intake, inventory management, warehouse operations, and customer notifications.

## Architecture

ShelfLife is composed of independently deployable microservices:

| Service | Port | Role |
|---------|------|------|
| web-gateway | 8080 | API gateway, rate limiting |
| order-service | 8081 | Order lifecycle management |
| fulfillment-engine | 8082 | Batch order processing |
| warehouse-api | 8083 | Stock mutations |
| notification-service | 8084 | Transactional email |
| analytics-service | 8085 | Event ingestion |
| auth-service | 8086 | JWT / API key auth |
| scheduler-service | 8087 | Cron job orchestration |
| inventory-cache | 6379 | Redis stock level cache |

See `docs/architecture.md` for the full system design.

## Quick Start

```bash
# Prerequisites: Docker Desktop, Python 3.11+, make

# Clone and setup
git clone git@github.com:shelflife/platform.git
cd platform
./setup-repo.sh

# Start all services
make up

# Verify health
make health

# Seed test data
make seed
```

## Development

```bash
make up              # Start services
make down            # Stop services
make test            # Run all tests
make lint            # Lint all services
make build           # Build Docker images
make logs            # Tail service logs
```

## Documentation

- [Architecture](docs/architecture.md)
- [Onboarding Guide](docs/onboarding.md)
- [ADRs](docs/adr/)
- [Runbooks](docs/runbooks/)
- [API Reference](docs/api/)

## Deployment

CI/CD is managed via GitHub Actions. Pushes to `main` trigger automatic deployment to production via the deploy workflow.

```bash
# Manual deploy (requires appropriate permissions)
./scripts/deploy.sh production
```

## Contributing

1. Create a feature branch from `main`.
2. Make your changes and add tests.
3. Open a PR using the pull request template.
4. Get review from a CODEOWNER.
5. Merge after CI passes.
