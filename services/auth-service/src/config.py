import os


class Settings:
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://auth:auth@auth-db:5432/auth")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
