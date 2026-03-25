"""Notification Service — FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .config import settings
from .email_sender import EmailSender, EmailMessage

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

sender: EmailSender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sender
    logger.info("notification-service starting")
    sender = EmailSender()
    yield
    await sender.close()


app = FastAPI(title="notification-service", lifespan=lifespan)


class SendNotificationRequest(BaseModel):
    to_email: str
    to_name: str
    template_name: str
    context: dict
    priority: bool = False


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.post("/api/notifications/send", status_code=202)
async def send_notification(req: SendNotificationRequest):
    """Queue a notification for delivery."""
    message = EmailMessage(
        to_email=req.to_email,
        to_name=req.to_name,
        template_name=req.template_name,
        context=req.context,
        priority=req.priority,
    )
    success = await sender.send(message)
    return {"queued": True, "delivered": success}


@app.get("/api/notifications/templates")
async def list_templates():
    """List available notification templates."""
    return {"templates": ["order_confirmation.html", "shipping_update.html"]}
