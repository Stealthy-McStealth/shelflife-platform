"""Web Gateway — rate limiting middleware."""

import time
import logging
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiter per client IP."""

    def __init__(self, app, rpm: int | None = None, burst: int | None = None):
        super().__init__(app)
        self._rpm = rpm or settings.RATE_LIMIT_RPM
        self._burst = burst or settings.RATE_LIMIT_BURST
        self._buckets: dict[str, dict] = defaultdict(
            lambda: {"tokens": self._burst, "last_refill": time.time()}
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/ready"):
            return await call_next(request)

        if not self._allow_request(client_ip):
            logger.warning(f"rate_limited ip={client_ip} path={request.url.path}")
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded", "retry_after_seconds": 60},
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        return response

    def _allow_request(self, client_ip: str) -> bool:
        bucket = self._buckets[client_ip]
        now = time.time()

        # Refill tokens based on elapsed time
        elapsed = now - bucket["last_refill"]
        refill_rate = self._rpm / 60.0
        bucket["tokens"] = min(self._burst, bucket["tokens"] + elapsed * refill_rate)
        bucket["last_refill"] = now

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For from load balancer
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
