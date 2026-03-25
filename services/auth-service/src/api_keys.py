"""Auth service — API key management."""

import hashlib
import logging
import secrets
from datetime import datetime
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manage API keys for service-to-service authentication."""

    def __init__(self):
        # In production, keys are stored in PostgreSQL
        self._keys: dict[str, dict] = {}

    def generate_key(self, service_name: str, scopes: list[str] | None = None) -> str:
        """Generate a new API key for a service."""
        raw_key = secrets.token_urlsafe(32)
        key_hash = self._hash_key(raw_key)

        self._keys[key_hash] = {
            "service": service_name,
            "scopes": scopes or [],
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
        }

        logger.info(f"api_key_created service={service_name}")
        return raw_key

    def validate_key(self, raw_key: str) -> Optional[dict]:
        """Validate an API key and return its metadata."""
        key_hash = self._hash_key(raw_key)
        record = self._keys.get(key_hash)

        if record is None:
            logger.warning("api_key_not_found")
            return None

        if not record["active"]:
            logger.warning(f"api_key_inactive service={record['service']}")
            return None

        return record

    def revoke_key(self, raw_key: str) -> bool:
        """Revoke an API key."""
        key_hash = self._hash_key(raw_key)
        if key_hash in self._keys:
            self._keys[key_hash]["active"] = False
            logger.info(f"api_key_revoked service={self._keys[key_hash]['service']}")
            return True
        return False

    def _hash_key(self, raw_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()
