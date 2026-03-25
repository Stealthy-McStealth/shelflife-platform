#!/usr/bin/env bash
set -euo pipefail

# Run tests across all services or a specific service
# Usage: ./scripts/run-tests.sh [service-name]

SERVICE="${1:-all}"
FAILED=0

run_service_tests() {
    local svc="$1"
    local svc_dir="services/$svc"

    if [ ! -d "$svc_dir/tests" ]; then
        echo "  [SKIP] $svc — no tests directory"
        return 0
    fi

    echo "  [TEST] $svc"
    pushd "$svc_dir" > /dev/null

    pip install -r requirements.txt -q 2>/dev/null
    pip install pytest pytest-asyncio httpx -q 2>/dev/null

    if python -m pytest tests/ -v --tb=short; then
        echo "  [PASS] $svc"
    else
        echo "  [FAIL] $svc"
        FAILED=$((FAILED + 1))
    fi

    popd > /dev/null
}

echo "=== ShelfLife Test Runner ==="
echo ""

if [ "$SERVICE" = "all" ]; then
    for svc_dir in services/*/; do
        svc=$(basename "$svc_dir")
        run_service_tests "$svc"
        echo ""
    done
else
    run_service_tests "$SERVICE"
fi

echo ""
if [ "$FAILED" -gt 0 ]; then
    echo "=== $FAILED service(s) failed ==="
    exit 1
else
    echo "=== All tests passed ==="
fi
