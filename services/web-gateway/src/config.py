import os


class Settings:
    ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8081")
    WAREHOUSE_API_URL = os.getenv("WAREHOUSE_API_URL", "http://warehouse-api:8083")
    FULFILLMENT_ENGINE_URL = os.getenv("FULFILLMENT_ENGINE_URL", "http://fulfillment-engine:8082")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8086")
    RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "120"))
    RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


settings = Settings()
