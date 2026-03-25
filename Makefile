.PHONY: up down build test lint logs health seed clean deploy

COMPOSE := docker compose

## Start all services
up:
	$(COMPOSE) up -d

## Stop all services
down:
	$(COMPOSE) down

## Build all Docker images
build:
	$(COMPOSE) build

## Run all tests
test:
	@for svc in services/*/; do \
		if [ -d "$$svc/tests" ]; then \
			echo "--- Testing $$svc ---"; \
			cd $$svc && pip install -r requirements.txt -q && python -m pytest tests/ -v; \
			cd ../..; \
		fi \
	done

## Run tests for a single service
test-service:
	cd services/$(SVC) && pip install -r requirements.txt -q && python -m pytest tests/ -v

## Run linters
lint:
	@for svc in services/*/; do \
		if [ -f "$$svc/src/app.py" ]; then \
			echo "--- Linting $$svc ---"; \
			python -m ruff check $$svc/src/; \
		fi \
	done

## Tail logs for all services
logs:
	$(COMPOSE) logs -f

## Check health of all services
health:
	@echo "Checking service health..."
	@curl -sf http://localhost:8080/health && echo " web-gateway: OK" || echo " web-gateway: FAIL"
	@curl -sf http://localhost:8081/health && echo " order-service: OK" || echo " order-service: FAIL"
	@curl -sf http://localhost:8082/health && echo " fulfillment-engine: OK" || echo " fulfillment-engine: FAIL"
	@curl -sf http://localhost:8083/health && echo " warehouse-api: OK" || echo " warehouse-api: FAIL"
	@curl -sf http://localhost:8084/health && echo " notification-service: OK" || echo " notification-service: FAIL"
	@curl -sf http://localhost:8085/health && echo " analytics-service: OK" || echo " analytics-service: FAIL"
	@curl -sf http://localhost:8086/health && echo " auth-service: OK" || echo " auth-service: FAIL"
	@curl -sf http://localhost:8087/health && echo " scheduler-service: OK" || echo " scheduler-service: FAIL"

## Seed local database
seed:
	./scripts/seed-db.sh

## Clean up containers and volumes
clean:
	$(COMPOSE) down -v --remove-orphans

## Deploy to environment (usage: make deploy ENV=production)
deploy:
	./scripts/deploy.sh $(ENV)
