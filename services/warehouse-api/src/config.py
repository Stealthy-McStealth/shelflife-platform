import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://warehouse:warehouse@warehouse-db:5432/inventory")
    REDIS_URL = os.getenv("REDIS_URL", "redis://inventory-cache:6379/0")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
    CACHE_WRITE_TIMEOUT_MS = int(os.getenv("CACHE_WRITE_TIMEOUT_MS", "500"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
