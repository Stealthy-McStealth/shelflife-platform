import os


class Settings:
    JOBS_FILE = os.getenv("JOBS_FILE", "/app/config/jobs.yaml")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))
    JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "300"))


settings = Settings()
