import os


class Settings:
    REDIS_URL = os.getenv("REDIS_URL", "redis://inventory-cache:6379/0")
    DEFAULT_TTL = int(os.getenv("CACHE_TTL", "3600"))
    MAX_MEMORY = os.getenv("REDIS_MAX_MEMORY", "512mb")
    EVICTION_POLICY = os.getenv("REDIS_EVICTION_POLICY", "noeviction")


settings = Settings()
