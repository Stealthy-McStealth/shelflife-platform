"""Scheduler Service — FastAPI application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .runner import JobRunner

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

runner = JobRunner()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("scheduler-service starting")
    runner.load_jobs()
    task = asyncio.create_task(_scheduler_loop())
    yield
    task.cancel()


app = FastAPI(title="scheduler-service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "scheduler-service"}


@app.get("/api/scheduler/jobs")
async def list_jobs():
    """List all configured scheduled jobs."""
    return {
        "jobs": [
            {
                "name": job.name,
                "schedule": job.schedule,
                "enabled": job.enabled,
                "command": job.command,
            }
            for job in runner.jobs
        ],
        "running": runner.running_count,
    }


@app.post("/api/scheduler/trigger/{job_name}")
async def trigger_job(job_name: str):
    """Manually trigger a scheduled job."""
    for job in runner.jobs:
        if job.name == job_name:
            executed = await runner.run_due_jobs()
            return {"triggered": job_name, "executed": executed}
    return {"error": f"job '{job_name}' not found"}, 404


@app.post("/api/scheduler/reload")
async def reload_jobs():
    """Reload job definitions from disk."""
    count = runner.load_jobs()
    return {"reloaded": True, "job_count": count}


async def _scheduler_loop():
    """Main scheduler loop — checks for due jobs every 60 seconds."""
    while True:
        try:
            executed = await runner.run_due_jobs()
            if executed:
                logger.info(f"scheduler_tick executed={executed}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"scheduler_loop_error error={e}")

        await asyncio.sleep(60)
