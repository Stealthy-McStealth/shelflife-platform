import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://orders:orders@orders-db:5432/orders")
    REDIS_URL = os.getenv("REDIS_URL", "redis://inventory-cache:6379/0")
    FULFILLMENT_QUEUE_URL = os.getenv("FULFILLMENT_QUEUE_URL", "sqs://fulfillment-queue")
    MAX_ITEMS_PER_ORDER = int(os.getenv("MAX_ITEMS_PER_ORDER", "100"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_PRIORITY_QUEUE = os.getenv("ENABLE_PRIORITY_QUEUE", "true").lower() == "true"


settings = Settings()
