#!/usr/bin/env bash
set -euo pipefail

# Deploy ShelfLife platform to the specified environment
# Usage: ./scripts/deploy.sh <environment>
#   environment: staging | production

ENVIRONMENT="${1:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REGISTRY="${ECR_REGISTRY:-}"
CLUSTER="shelflife-${ENVIRONMENT}"
GIT_SHA=$(git rev-parse --short HEAD)

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: ./scripts/deploy.sh <environment>"
    echo "  environment: staging | production"
    exit 1
fi

if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Error: environment must be 'staging' or 'production'"
    exit 1
fi

if [ -z "$ECR_REGISTRY" ]; then
    echo "Error: ECR_REGISTRY environment variable is required"
    exit 1
fi

SERVICES=(
    web-gateway
    order-service
    fulfillment-engine
    warehouse-api
    notification-service
    analytics-service
    auth-service
    scheduler-service
)

echo "=== ShelfLife Deploy ==="
echo "Environment: $ENVIRONMENT"
echo "Cluster: $CLUSTER"
echo "Git SHA: $GIT_SHA"
echo "Region: $AWS_REGION"
echo ""

# Build and push images
echo "--- Building and pushing images ---"
for svc in "${SERVICES[@]}"; do
    echo "  Building $svc..."
    docker build -t "$ECR_REGISTRY/shelflife/$svc:$GIT_SHA" \
                 -t "$ECR_REGISTRY/shelflife/$svc:latest" \
                 "services/$svc/"
    docker push "$ECR_REGISTRY/shelflife/$svc:$GIT_SHA"
    docker push "$ECR_REGISTRY/shelflife/$svc:latest"
done

echo ""
echo "--- Updating ECS services ---"
for svc in "${SERVICES[@]}"; do
    echo "  Deploying $svc..."
    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$svc" \
        --force-new-deployment \
        --region "$AWS_REGION" \
        --output text --query 'service.serviceName'
done

echo ""
echo "--- Waiting for services to stabilize ---"
for svc in "${SERVICES[@]}"; do
    echo "  Waiting for $svc..."
    aws ecs wait services-stable \
        --cluster "$CLUSTER" \
        --services "$svc" \
        --region "$AWS_REGION"
done

echo ""
echo "=== Deploy complete: $GIT_SHA -> $ENVIRONMENT ==="
