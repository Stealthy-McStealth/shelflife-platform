"""Auth Service — FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

from .config import settings
from .jwt_handler import JWTHandler
from .api_keys import APIKeyManager

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

jwt_handler = JWTHandler()
api_key_manager = APIKeyManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("auth-service starting")
    yield


app = FastAPI(title="auth-service", lifespan=lifespan)


class TokenRequest(BaseModel):
    subject: str
    scopes: list[str] = []


class TokenResponse(BaseModel):
    token: str
    expires_in_minutes: int


class APIKeyRequest(BaseModel):
    service_name: str
    scopes: list[str] = []


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth-service"}


@app.post("/api/auth/token", response_model=TokenResponse)
async def create_token(req: TokenRequest):
    """Issue a new JWT token."""
    token = jwt_handler.create_token(req.subject, req.scopes)
    return TokenResponse(token=token, expires_in_minutes=settings.JWT_EXPIRY_MINUTES)


@app.post("/api/auth/verify")
async def verify_token(authorization: str = Header(...)):
    """Verify a JWT token from the Authorization header."""
    token = authorization.removeprefix("Bearer ").strip()
    payload = jwt_handler.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    return {"valid": True, "subject": payload["sub"], "scopes": payload.get("scopes", [])}


@app.post("/api/auth/refresh")
async def refresh_token(authorization: str = Header(...)):
    """Refresh an existing JWT token."""
    token = authorization.removeprefix("Bearer ").strip()
    new_token = jwt_handler.refresh_token(token)
    if new_token is None:
        raise HTTPException(status_code=401, detail="cannot refresh invalid token")
    return TokenResponse(token=new_token, expires_in_minutes=settings.JWT_EXPIRY_MINUTES)


@app.post("/api/auth/keys")
async def create_api_key(req: APIKeyRequest):
    """Generate a new API key for a service."""
    key = api_key_manager.generate_key(req.service_name, req.scopes)
    return {"api_key": key, "service": req.service_name}


@app.delete("/api/auth/keys")
async def revoke_api_key(x_api_key: str = Header(...)):
    """Revoke an API key."""
    success = api_key_manager.revoke_key(x_api_key)
    if not success:
        raise HTTPException(status_code=404, detail="key not found")
    return {"revoked": True}
