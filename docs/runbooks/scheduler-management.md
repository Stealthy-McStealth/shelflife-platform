# Runbook: Scheduler Service Management

## Service Overview

The scheduler-service reads job definitions from `jobs.yaml` and executes them on cron schedules. It runs as a single-replica deployment to prevent duplicate execution.

## Configured Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| order-cleanup | `0 2 * * *` | Remove stale pending orders older than 30 days |
| analytics-rollup | `0 */6 * * *` | Aggregate raw events into hourly/daily rollups |
| health-check-sweep | `*/5 * * * *` | Ping all service health endpoints |

## Common Operations

### View Current Jobs

```bash
curl http://scheduler-service:8087/api/scheduler/jobs
```

### Manually Trigger a Job

```bash
curl -X POST http://scheduler-service:8087/api/scheduler/trigger/order-cleanup
curl -X POST http://scheduler-service:8087/api/scheduler/trigger/analytics-rollup
curl -X POST http://scheduler-service:8087/api/scheduler/trigger/health-check-sweep
```

### Reload Job Definitions

After updating `jobs.yaml` in the ConfigMap:

```bash
# Update the ConfigMap
kubectl create configmap scheduler-jobs \
  --from-file=jobs.yaml=infra/scheduler/jobs.yaml \
  -n shelflife --dry-run=client -o yaml | kubectl apply -f -

# Tell the scheduler to reload
curl -X POST http://scheduler-service:8087/api/scheduler/reload
```

### Check Scheduler Logs

```bash
kubectl logs -l app=scheduler-service -n shelflife --tail=100

# Filter for specific job
kubectl logs -l app=scheduler-service -n shelflife | grep "order-cleanup"
```

## Troubleshooting

### Job Not Executing on Schedule

1. Verify the job is enabled in `jobs.yaml`.
2. Check that the scheduler pod is running and not in CrashLoopBackOff.
3. Verify the cron expression is valid.
4. Check if `MAX_CONCURRENT_JOBS` has been reached.

```bash
kubectl logs -l app=scheduler-service -n shelflife | grep "max_concurrent_reached"
```

### Job Timing Out

The default timeout is 300 seconds (5 minutes). If a job needs more time:

1. Update `timeout` in `jobs.yaml` for that job.
2. Reload the scheduler configuration.

### Job Failing Repeatedly

```bash
# Check recent failures
kubectl logs -l app=scheduler-service -n shelflife | grep "job_failed"

# Check stderr output
kubectl logs -l app=scheduler-service -n shelflife | grep "job_error"
```

Common causes:
- Missing dependencies in the job script's environment.
- Network connectivity issues (e.g., health-check-sweep cannot reach a service).
- Database connectivity issues (e.g., order-cleanup cannot reach the orders DB).

## Adding a New Job

1. Add the job definition to `infra/scheduler/jobs.yaml`:
   ```yaml
   - name: my-new-job
     schedule: "0 */12 * * *"
     command: "python -m scripts.my_new_job"
     timeout: 300
     enabled: true
     description: "Description of what this job does"
   ```

2. Apply the ConfigMap update and reload (see "Reload Job Definitions" above).

## Escalation

For scheduler issues, escalate to `#platform-eng` with the scheduler pod logs and the current `jobs.yaml` content.
