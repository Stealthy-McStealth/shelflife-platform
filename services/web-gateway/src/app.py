"""Web Gateway — public-facing API gateway."""

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware import RateLimitMiddleware

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("web-gateway starting")
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    yield
    await app.state.http_client.aclose()


app = FastAPI(title="web-gateway", lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "web-gateway"}


@app.get("/ready")
async def readiness():
    """Readiness probe — checks downstream services."""
    return {"status": "ready"}


@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_orders(request: Request, path: str = ""):
    """Proxy requests to order-service."""
    return await _proxy_request(request, settings.ORDER_SERVICE_URL, f"/api/orders/{path}")


@app.api_route("/api/stock/{path:path}", methods=["GET", "POST", "PUT"])
async def proxy_stock(request: Request, path: str = ""):
    """Proxy requests to warehouse-api."""
    return await _proxy_request(request, settings.WAREHOUSE_API_URL, f"/api/stock/{path}")


async def _proxy_request(request: Request, upstream_url: str, path: str):
    """Forward a request to an upstream service."""
    client: httpx.AsyncClient = request.app.state.http_client
    url = f"{upstream_url}{path}"

    try:
        body = await request.body()
        response = await client.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=body if body else None,
            params=dict(request.query_params),
        )
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"proxy_timeout upstream={upstream_url} path={path}")
        raise HTTPException(status_code=504, detail="upstream timeout")
    except httpx.ConnectError:
        logger.error(f"proxy_connect_error upstream={upstream_url} path={path}")
        raise HTTPException(status_code=502, detail="upstream unavailable")
