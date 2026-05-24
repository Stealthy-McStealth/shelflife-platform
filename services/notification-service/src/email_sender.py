"""Notification service — email delivery with exponential backoff."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from .config import settings
from .templates import render_template, get_subject_line

logger = logging.getLogger(__name__)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


@dataclass
class EmailMessage:
    to_email: str
    to_name: str
    template_name: str
    context: dict
    priority: bool = False


class EmailSender:
    """SendGrid email sender with exponential backoff retry."""

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        self._max_retries = settings.MAX_RETRIES
        self._base_backoff_ms = settings.BASE_BACKOFF_MS

    async def send(self, message: EmailMessage) -> bool:
        """Send an email with retry and exponential backoff."""
        body_html = render_template(message.template_name, message.context)
        subject = get_subject_line(message.template_name, message.context)

        payload = {
            "personalizations": [{"to": [{"email": message.to_email, "name": message.to_name}]}],
            "from": {"email": settings.SENDGRID_FROM_EMAIL, "name": settings.SENDGRID_FROM_NAME},
            "subject": subject,
            "content": [{"type": "text/html", "value": body_html}],
        }

        for attempt in range(self._max_retries):
            try:
                response = await self._client.post(SENDGRID_API_URL, json=payload)

                if response.status_code in (200, 202):
                    logger.info(
                        f"email_sent to={message.to_email} template={message.template_name} "
                        f"attempt={attempt + 1}"
                    )
                    return True

                if response.status_code == 429 or response.status_code >= 500:
                    # Retryable error — back off
                    backoff_ms = self._base_backoff_ms * (2 ** attempt)
                    logger.warning(
                        f"email_retry status={response.status_code} attempt={attempt + 1} "
                        f"backoff_ms={backoff_ms}"
                    )
                    await asyncio.sleep(backoff_ms / 1000)
                    continue

                # Non-retryable error
                logger.error(
                    f"email_failed status={response.status_code} to={message.to_email} "
                    f"body={response.text}"
                )
                return False

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                backoff_ms = self._base_backoff_ms * (2 ** attempt)
                logger.warning(
                    f"email_network_error error={e} attempt={attempt + 1} backoff_ms={backoff_ms}"
                )
                await asyncio.sleep(backoff_ms / 1000)

        logger.error(f"email_exhausted_retries to={message.to_email} template={message.template_name}")
        return False

    async def close(self):
        await self._client.aclose()

# Exponential backoff added for SendGrid 429 responses.
# Max retries: 5, base delay: 1s, max delay: 32s

