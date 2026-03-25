"""Scheduler service — cron job runner."""

import asyncio
import logging
from datetime import datetime
from typing import Any

import yaml
from croniter import croniter

from .config import settings

logger = logging.getLogger(__name__)


class JobDefinition:
    def __init__(self, name: str, schedule: str, command: str, timeout: int, enabled: bool = True):
        self.name = name
        self.schedule = schedule
        self.command = command
        self.timeout = timeout
        self.enabled = enabled


class JobRunner:
    """Reads jobs from jobs.yaml and executes them on cron schedules."""

    def __init__(self):
        self._jobs: list[JobDefinition] = []
        self._running: dict[str, asyncio.Task] = {}

    def load_jobs(self, jobs_file: str | None = None) -> int:
        """Load job definitions from YAML config."""
        path = jobs_file or settings.JOBS_FILE
        try:
            with open(path) as f:
                config = yaml.safe_load(f)

            self._jobs = []
            for job_config in config.get("jobs", []):
                job = JobDefinition(
                    name=job_config["name"],
                    schedule=job_config["schedule"],
                    command=job_config["command"],
                    timeout=job_config.get("timeout", settings.JOB_TIMEOUT_SECONDS),
                    enabled=job_config.get("enabled", True),
                )
                self._jobs.append(job)

            logger.info(f"jobs_loaded count={len(self._jobs)} file={path}")
            return len(self._jobs)

        except FileNotFoundError:
            logger.error(f"jobs_file_not_found path={path}")
            return 0
        except yaml.YAMLError as e:
            logger.error(f"jobs_parse_error error={e}")
            return 0

    async def run_due_jobs(self) -> list[str]:
        """Check all jobs and run those that are due."""
        now = datetime.utcnow()
        executed = []

        for job in self._jobs:
            if not job.enabled:
                continue
            if job.name in self._running:
                continue
            if len(self._running) >= settings.MAX_CONCURRENT_JOBS:
                logger.warning(f"max_concurrent_reached skipping={job.name}")
                break

            if self._is_due(job, now):
                task = asyncio.create_task(self._execute_job(job))
                self._running[job.name] = task
                executed.append(job.name)

        return executed

    def _is_due(self, job: JobDefinition, now: datetime) -> bool:
        """Check if a job is due based on its cron schedule."""
        try:
            cron = croniter(job.schedule, now)
            prev = cron.get_prev(datetime)
            # Consider job due if the previous scheduled time is within the last 60 seconds
            return (now - prev).total_seconds() < 60
        except (ValueError, KeyError):
            logger.error(f"invalid_cron job={job.name} schedule={job.schedule}")
            return False

    async def _execute_job(self, job: JobDefinition) -> None:
        """Execute a single job with timeout handling."""
        logger.info(f"job_start name={job.name} command={job.command}")
        start = datetime.utcnow()

        try:
            proc = await asyncio.create_subprocess_shell(
                job.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=job.timeout)

            elapsed_ms = (datetime.utcnow() - start).total_seconds() * 1000
            if proc.returncode == 0:
                logger.info(f"job_success name={job.name} elapsed_ms={elapsed_ms:.0f}")
            else:
                logger.error(
                    f"job_failed name={job.name} exit_code={proc.returncode} "
                    f"stderr={stderr.decode()[:200]}"
                )

        except asyncio.TimeoutError:
            logger.error(f"job_timeout name={job.name} timeout={job.timeout}s")
        except Exception as e:
            logger.error(f"job_error name={job.name} error={e}")
        finally:
            self._running.pop(job.name, None)

    @property
    def jobs(self) -> list[JobDefinition]:
        return self._jobs

    @property
    def running_count(self) -> int:
        return len(self._running)
