#!/bin/bash
# Setup script for ShelfLife platform GitHub repository
# Creates commit history with proper dates/authors and PRs via gh CLI
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Repository created: gh repo create Stealthy-McStealth/shelflife-platform --public
#   - Run this script from the shelflife-platform/ directory
#
# Usage:
#   cd shelflife-platform
#   chmod +x setup-repo.sh
#   ./setup-repo.sh

set -e

ORG="Stealthy-McStealth"
REPO="shelflife-platform"
REMOTE="origin"

# Author identities
SARAH="Sarah Chen <sarah.chen@shelflife.io>"
DANA="Dana Kim <dana.kim@shelflife.io>"
MIKE="Mike Ross <mike.ross@shelflife.io>"
TOM="Tom Ashworth <tom.ashworth@shelflife.io>"
JAKE="Jake Morrison <jake.morrison@shelflife.io>"
ALEX="Alex Volkov <alex.volkov@shelflife.io>"
PRIYA="Priya Patel <priya.patel@shelflife.io>"

echo "=== ShelfLife Platform Repo Setup ==="
echo ""
echo "This script will:"
echo "  1. Initialize git repo"
echo "  2. Create commit history with realistic dates and authors"
echo "  3. Push to GitHub"
echo "  4. Create merged PRs"
echo ""
echo "Make sure you've created the repo first:"
echo "  gh repo create $ORG/$REPO --public --description 'ShelfLife platform monorepo'"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

# ============================================================
# PHASE 1: Initial commit (base codebase ~2 months ago)
# ============================================================

echo "--- Phase 1: Initial commit ---"

git init
git checkout -b main

# Add all current files as the initial state
git add .
GIT_AUTHOR_DATE="2026-03-25T10:00:00Z" GIT_COMMITTER_DATE="2026-03-25T10:00:00Z" \
  git -c user.name="Dana Kim" -c user.email="dana.kim@shelflife.io" \
  commit -m "Initial platform structure

Set up ShelfLife platform monorepo with core services:
- fulfillment-engine: order processing and stock checking
- order-service: order creation and lifecycle
- warehouse-api: stock mutations and cache write-through
- inventory-cache: Redis client library
- web-gateway: API routing
- notification-service: email/SMS delivery
- analytics-service: event ingestion
- auth-service: JWT authentication
- scheduler-service: cron job runner

Infrastructure:
- Terraform configs for AWS (ECS, ElastiCache, RDS)
- Kubernetes manifests
- CI/CD workflows
- Docker Compose for local development"

echo "--- Phase 1 complete ---"

# ============================================================
# PHASE 2: Add commits over time to build realistic history
# We'll create branches, commit, merge to simulate PRs
# ============================================================

echo "--- Phase 2: Building commit history ---"

# Helper function for creating a commit with specific date and author
make_commit() {
  local date="$1"
  local author_name="$2"
  local author_email="$3"
  local message="$4"

  git add -A
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
    git -c user.name="$author_name" -c user.email="$author_email" \
    commit -m "$message" --allow-empty
}

# Helper to create a PR-like merge commit
merge_pr() {
  local branch="$1"
  local date="$2"
  local author_name="$3"
  local author_email="$4"
  local pr_num="$5"
  local title="$6"

  git checkout main
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
    git -c user.name="$author_name" -c user.email="$author_email" \
    merge --no-ff "$branch" -m "Merge pull request #$pr_num from $ORG/$branch

$title"
  git branch -d "$branch"
}

# --- PR #10: Early features (auth improvements) ---
git checkout -b feat/api-key-rotation
# (files already exist from initial commit, we simulate the PR being part of history)
make_commit "2026-04-01T09:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "feat: add API key rotation support

Implements automatic key rotation for service-to-service auth.
Keys can be rotated without downtime using the dual-key window."
merge_pr "feat/api-key-rotation" "2026-04-01T14:00:00Z" "Dana Kim" "dana.kim@shelflife.io" 10 "feat: add API key rotation support"

# --- PR #11-15: Various maintenance (simulated as single commits on main) ---
make_commit "2026-04-05T11:00:00Z" "Sarah Chen" "sarah.chen@shelflife.io" \
  "chore: add integration tests for order-service (#11)"

make_commit "2026-04-08T16:00:00Z" "Mike Ross" "mike.ross@shelflife.io" \
  "fix: order-service timeout on large batch queries (#12)"

make_commit "2026-04-12T10:30:00Z" "Priya Patel" "priya.patel@shelflife.io" \
  "chore: update notification-service SendGrid SDK to v7 (#13)"

make_commit "2026-04-15T14:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "docs: add runbook for cache operations (#14)"

make_commit "2026-04-18T09:00:00Z" "Jake Morrison" "jake.morrison@shelflife.io" \
  "feat: add order status webhook callbacks (#15)"

# --- PR #16: Scheduler timeout fix ---
git checkout -b fix/scheduler-timeout
make_commit "2026-04-28T11:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "fix: scheduler job timeout handling edge case

Fixed race condition where a job could be marked as timed out
even after successful completion if the response arrived during
the timeout check window."
merge_pr "fix/scheduler-timeout" "2026-04-28T15:00:00Z" "Dana Kim" "dana.kim@shelflife.io" 16 "fix: scheduler job timeout handling edge case"

# --- PR #17-18: More maintenance ---
make_commit "2026-04-30T10:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "feat: API key rotation support for auth-service (#17)"

make_commit "2026-05-02T13:30:00Z" "Priya Patel" "priya.patel@shelflife.io" \
  "chore: update notification-service dependencies (#18)"

# --- PR #19: ADR-004 priority orders ---
git checkout -b docs/adr-004
make_commit "2026-05-06T12:00:00Z" "Jake Morrison" "jake.morrison@shelflife.io" \
  "docs: add ADR-004 priority order processing

Documents the decision to implement priority queuing for premium
customers in the fulfillment pipeline."
merge_pr "docs/adr-004" "2026-05-06T16:00:00Z" "Jake Morrison" "jake.morrison@shelflife.io" 19 "docs: add ADR-004 priority order processing"

# --- PR #20: Terraform update ---
make_commit "2026-05-07T14:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "chore: update Terraform provider versions (#20)"

# --- PR #21: Warehouse audit log ---
git checkout -b feat/audit-log
make_commit "2026-05-08T12:00:00Z" "Mike Ross" "mike.ross@shelflife.io" \
  "feat: add warehouse stock adjustment audit log

All stock adjustments now emit audit events to analytics-service
for compliance tracking. Includes adjustment reason, user, and delta."
merge_pr "feat/audit-log" "2026-05-08T16:00:00Z" "Mike Ross" "mike.ross@shelflife.io" 21 "feat: add warehouse stock adjustment audit log"

# --- PR #22: Analytics memory leak fix ---
git checkout -b fix/analytics-buffer
make_commit "2026-05-09T15:20:00Z" "Sarah Chen" "sarah.chen@shelflife.io" \
  "fix: analytics-service memory leak in event buffer

Event buffer wasn't being flushed properly when the ClickHouse
connection timed out. Added proper drain on connection reset and
bounded the buffer size to prevent OOM."
merge_pr "fix/analytics-buffer" "2026-05-09T17:00:00Z" "Sarah Chen" "sarah.chen@shelflife.io" 22 "fix: analytics-service memory leak in event buffer"

# ============================================================
# PR #23: THE CRITICAL ONE — remove unused scheduled tasks
# This is what the player must find
# ============================================================

git checkout -b chore/cleanup-scheduler-jobs

# Modify jobs.yaml to contain the OLD state (with inventory-sync) temporarily
# so the diff shows removal
cat > infra/scheduler/jobs.yaml << 'JOBS_WITH_SYNC'
# Scheduled tasks for ShelfLife platform
# Managed by scheduler-service. Changes require deploy.

jobs:
  - name: inventory-sync
    schedule: "*/30 * * * *"
    command: shelflife-jobs
    args:
      - sync
      - --source warehouse-db
      - --target inventory-cache
      - --type full-refresh
    timeout: 120s
    alert_on_failure: false
    description: "Periodic full refresh of inventory cache from warehouse DB"

  - name: report-daily-summary
    schedule: "0 6 * * *"
    command: shelflife-jobs
    args:
      - report
      - --source analytics-db
      - --target email
      - --type daily-summary
    timeout: 300s
    alert_on_failure: false
    description: "Daily summary report sent to ops team"

  - name: cache-warmup-legacy
    schedule: "0 5 * * *"
    command: shelflife-jobs
    args:
      - warmup
      - --source warehouse-db
      - --target inventory-cache
      - --type lazy-load
    timeout: 600s
    alert_on_failure: false
    description: "Legacy cache warmup (deprecated - lazy loading handles this now)"

  - name: metrics-rollup-hourly
    schedule: "0 * * * *"
    command: shelflife-jobs
    args:
      - rollup
      - --source metrics-raw
      - --target metrics-db
      - --type aggregate
    timeout: 120s
    alert_on_failure: false
    description: "Hourly metrics rollup (replaced by analytics-service aggregation)"

  - name: order-cleanup
    schedule: "0 3 * * *"
    command: shelflife-jobs
    args:
      - cleanup
      - --source order-db
      - --type delete-expired
      - --older-than 90d
    timeout: 300s
    alert_on_failure: true
    description: "Remove expired/cancelled orders older than 90 days"

  - name: analytics-rollup
    schedule: "0 * * * *"
    command: shelflife-jobs
    args:
      - rollup
      - --source analytics-events
      - --target analytics-db
      - --type aggregate
    timeout: 60s
    alert_on_failure: true
    description: "Hourly aggregation of raw analytics events"

  - name: health-check-sweep
    schedule: "*/5 * * * *"
    command: shelflife-jobs
    args:
      - health
      - --source all-services
      - --target status-page
      - --type ping
    timeout: 30s
    alert_on_failure: true
    description: "Sweep all service health endpoints"
JOBS_WITH_SYNC

git add -A
GIT_AUTHOR_DATE="2026-05-10T10:00:00Z" GIT_COMMITTER_DATE="2026-05-10T10:00:00Z" \
  git -c user.name="Tom Ashworth" -c user.email="tom.ashworth@shelflife.io" \
  commit -m "temp: show old jobs.yaml state for diff"

# Now apply the removal (this creates the PR diff the player will see)
cat > infra/scheduler/jobs.yaml << 'JOBS_CLEANED'
# Scheduled tasks for ShelfLife platform
# Managed by scheduler-service. Changes require deploy.

jobs:
  - name: order-cleanup
    schedule: "0 3 * * *"
    command: shelflife-jobs
    args:
      - cleanup
      - --source order-db
      - --type delete-expired
      - --older-than 90d
    timeout: 300s
    alert_on_failure: true
    description: "Remove expired/cancelled orders older than 90 days"

  - name: analytics-rollup
    schedule: "0 * * * *"
    command: shelflife-jobs
    args:
      - rollup
      - --source analytics-events
      - --target analytics-db
      - --type aggregate
    timeout: 60s
    alert_on_failure: true
    description: "Hourly aggregation of raw analytics events"

  - name: health-check-sweep
    schedule: "*/5 * * * *"
    command: shelflife-jobs
    args:
      - health
      - --source all-services
      - --target status-page
      - --type ping
    timeout: 30s
    alert_on_failure: true
    description: "Sweep all service health endpoints"
JOBS_CLEANED

git add -A
GIT_AUTHOR_DATE="2026-05-10T11:23:41Z" GIT_COMMITTER_DATE="2026-05-10T11:23:41Z" \
  git -c user.name="Tom Ashworth" -c user.email="tom.ashworth@shelflife.io" \
  commit -m "chore: remove unused scheduled tasks

Cleanup of scheduler jobs that haven't triggered any failure alerts
in the past 6 months. These appear to be legacy jobs from earlier
architecture iterations that are no longer needed.

Removed:
- inventory-sync — no alerts since creation, cache is maintained via write-through
- report-daily-summary — replaced by Datadog dashboards in Q1
- cache-warmup-legacy — deprecated when we moved to lazy loading
- metrics-rollup-hourly — replaced by analytics-service aggregation

Reviewed-by: Dana Kim <dana.kim@shelflife.io>"

merge_pr "chore/cleanup-scheduler-jobs" "2026-05-10T14:12:00Z" "Tom Ashworth" "tom.ashworth@shelflife.io" 23 "chore: remove unused scheduled tasks"

# ============================================================
# Continue with PRs after the critical one
# ============================================================

# --- PR #24: Batch optimization (RED HERRING) ---
git checkout -b perf/batch-mutations
make_commit "2026-05-12T10:45:00Z" "Alex Volkov" "alex.volkov@shelflife.io" \
  "perf: batch stock mutations for improved throughput

Groups up to 50 stock mutations into a single DB transaction.
Cache writes are still per-item to maintain consistency.

Benchmarks show 3x throughput improvement during peak receiving
operations. Individual cache write latency unchanged."
merge_pr "perf/batch-mutations" "2026-05-12T14:00:00Z" "Alex Volkov" "alex.volkov@shelflife.io" 24 "perf: batch stock mutations for improved throughput"

# --- PR #25: Redis client upgrade ---
make_commit "2026-05-14T08:30:00Z" "Tom Ashworth" "tom.ashworth@shelflife.io" \
  "chore: upgrade Redis client to 5.x (#25)

Major version bump for redis-py. API is mostly compatible,
updated connection initialization across services."

# --- PR #26: Priority queue (RED HERRING) ---
git checkout -b feat/priority-queue
make_commit "2026-05-17T14:22:00Z" "Jake Morrison" "jake.morrison@shelflife.io" \
  "feat: add priority queue for premium orders

Premium customers now get their orders processed first within each
batch cycle. Standard orders are still processed normally — just
after premium orders in the same batch. This does not affect whether
orders are fulfilled or skipped."
merge_pr "feat/priority-queue" "2026-05-17T16:00:00Z" "Jake Morrison" "jake.morrison@shelflife.io" 26 "feat: add priority queue for premium orders"

# --- PR #27: notification retry fix ---
make_commit "2026-05-17T09:00:00Z" "Priya Patel" "priya.patel@shelflife.io" \
  "fix: notification-service retry logic for SendGrid rate limits (#27)

Implements exponential backoff when SendGrid returns 429.
Previously we'd just fail the batch."

# --- PR #28: Onboarding docs ---
make_commit "2026-05-19T09:00:00Z" "Dana Kim" "dana.kim@shelflife.io" \
  "docs: update onboarding guide for new hires (#28)"

# --- PR #29: Datadog APM ---
make_commit "2026-05-19T11:30:00Z" "Mike Ross" "mike.ross@shelflife.io" \
  "feat: add Datadog APM traces to fulfillment-engine (#29)"

# --- PR #30: FastAPI bump ---
make_commit "2026-05-20T10:00:00Z" "dependabot[bot]" "dependabot@github.com" \
  "chore: bump fastapi to 0.111.0 (#30)"

# --- PR #31: Null SKU fix ---
git checkout -b fix/null-sku-validation
make_commit "2026-05-21T09:14:00Z" "Sarah Chen" "sarah.chen@shelflife.io" \
  "fix: handle null SKU in order validation

Null SKU was being passed through to fulfillment-engine causing
silent queue drops. Added validation at the handler level.

Fixes #142."
merge_pr "fix/null-sku-validation" "2026-05-21T11:00:00Z" "Sarah Chen" "sarah.chen@shelflife.io" 31 "fix: handle null SKU in order validation"

echo "--- Phase 2 complete ---"

# ============================================================
# PHASE 3: Push to GitHub
# ============================================================

echo "--- Phase 3: Push to GitHub ---"
echo ""
echo "Ready to push. Run these commands manually:"
echo ""
echo "  git remote add origin git@github.com:$ORG/$REPO.git"
echo "  git push -u origin main"
echo ""
echo "Then create PRs on GitHub using gh CLI:"
echo ""
echo "Note: Since we used merge commits, the PR history is visible in git log."
echo "For a more realistic look, you can create actual PRs via the GitHub UI"
echo "or use 'gh pr create' on temporary branches."
echo ""
echo "=== Setup complete ==="
