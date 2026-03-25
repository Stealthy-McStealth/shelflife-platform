import os


class Settings:
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "orders@shelflife.io")
    SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ShelfLife")
    TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")
    MAX_RETRIES = int(os.getenv("EMAIL_MAX_RETRIES", "5"))
    BASE_BACKOFF_MS = int(os.getenv("EMAIL_BASE_BACKOFF_MS", "500"))
    QUEUE_URL = os.getenv("NOTIFICATION_QUEUE_URL", "sqs://notification-queue")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
