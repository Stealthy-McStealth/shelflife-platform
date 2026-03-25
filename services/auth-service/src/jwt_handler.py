"""Auth service — JWT token management."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt

from .config import settings

logger = logging.getLogger(__name__)


class JWTHandler:
    """Issue and verify JWT tokens for service authentication."""

    def __init__(self):
        self._secret = settings.JWT_SECRET
        self._algorithm = settings.JWT_ALGORITHM
        self._expiry_minutes = settings.JWT_EXPIRY_MINUTES

    def create_token(self, subject: str, scopes: list[str] | None = None) -> str:
        """Create a signed JWT token."""
        now = datetime.utcnow()
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expiry_minutes),
            "scopes": scopes or [],
        }
        token = jwt.encode(payload, self._secret, algorithm=self._algorithm)
        logger.info(f"token_created subject={subject} expires_in={self._expiry_minutes}m")
        return token

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token. Returns None if invalid."""
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("token_expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"token_invalid error={e}")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """Issue a new token if the existing one is still valid."""
        payload = self.verify_token(token)
        if payload is None:
            return None
        return self.create_token(payload["sub"], payload.get("scopes"))
