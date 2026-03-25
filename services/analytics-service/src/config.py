import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://analytics:analytics@analytics-db:5432/analytics")
    BUFFER_MAX_SIZE = int(os.getenv("BUFFER_MAX_SIZE", "10000"))
    FLUSH_INTERVAL_SECONDS = int(os.getenv("FLUSH_INTERVAL_SECONDS", "30"))
    FLUSH_BATCH_SIZE = int(os.getenv("FLUSH_BATCH_SIZE", "500"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
