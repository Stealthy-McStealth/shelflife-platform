import os


class Settings:
    REDIS_URL = os.getenv("REDIS_URL", "redis://inventory-cache:6379/0")
    QUEUE_URL = os.getenv("FULFILLMENT_QUEUE_URL", "sqs://fulfillment-queue")
    SKIP_ZERO_STOCK = os.getenv("SKIP_ZERO_STOCK", "true").lower() == "true"
    QUEUE_BATCH_SIZE = int(os.getenv("QUEUE_BATCH_SIZE", "50"))
    PROCESSING_INTERVAL_MS = int(os.getenv("PROCESSING_INTERVAL_MS", "500"))
    MAX_RETRY_COUNT = int(os.getenv("MAX_RETRY_COUNT", "3"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DATADOG_ENABLED = os.getenv("DD_TRACE_ENABLED", "false").lower() == "true"


settings = Settings()
