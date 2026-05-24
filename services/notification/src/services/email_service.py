"""メール送信サービス"""

import logging

import aiosmtplib
from jinja2 import BaseLoader, Environment

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

env = Environment(loader=BaseLoader())


async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
) -> bool:
    smtp_host = smtp_host or settings.SMTP_HOST
    smtp_port = smtp_port or settings.SMTP_PORT

    message = f"""From: {settings.SMTP_FROM_EMAIL}
To: {to_email}
Subject: {subject}
Content-Type: text/html; charset=utf-8

{body_html}
"""

    try:
        if not settings.SMTP_USER:
            logger.warning("SMTP_USER not configured — skipping email send to %s", to_email)
            return False

        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=settings.SMTP_USE_TLS,
        )
        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
        return False


def render_email_body(body_template: str, variables: dict) -> str:
    template = env.from_string(body_template)
    return template.render(**variables)
