"""Notification service — template rendering."""

import os
import logging
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)

_template_cache: dict[str, str] = {}


def render_template(template_name: str, context: dict) -> str:
    """Render an HTML template with the given context variables."""
    template = _load_template(template_name)

    # Simple variable substitution using {{variable}} syntax
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))

    return template


def _load_template(template_name: str) -> str:
    """Load a template from disk with caching."""
    if template_name in _template_cache:
        return _template_cache[template_name]

    template_path = Path(settings.TEMPLATE_DIR) / template_name
    if not template_path.exists():
        logger.error(f"template_not_found name={template_name}")
        raise FileNotFoundError(f"Template not found: {template_name}")

    content = template_path.read_text()
    _template_cache[template_name] = content
    logger.debug(f"template_loaded name={template_name}")
    return content


def get_subject_line(template_name: str, context: dict) -> str:
    """Generate email subject based on template type."""
    subjects = {
        "order_confirmation.html": f"Order Confirmed — #{context.get('order_id', '')}",
        "shipping_update.html": f"Your order #{context.get('order_id', '')} has shipped",
    }
    return subjects.get(template_name, "ShelfLife Notification")
