"""desknet's NEO通知配送adapter。

NEOの契約差分をNotification Serviceから隔離するため、接続先は設定で注入する。
"""

import logging

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


async def deliver_to_neo(notification) -> bool | None:
    """通知をNEO APIへ配送する。未設定時はNone、配送失敗時はFalseを返す。"""
    settings = get_settings()
    if "neo" not in (notification.channels or []):
        return None
    if not settings.NEO_ENABLED:
        return None
    if not settings.NEO_API_URL or not settings.NEO_API_KEY:
        logger.error("NEO is enabled but API URL or API key is missing")
        return False

    payload = {
        "recipient_id": str(notification.recipient_id),
        "subject": notification.title,
        "body": notification.body,
        "metadata": notification.metadata_ or {},
        "idempotency_key": notification.idempotency_key,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.NEO_TIMEOUT_SECONDS) as client:
            response = await client.post(
                settings.NEO_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.NEO_API_KEY}",
                    "Idempotency-Key": notification.idempotency_key or "",
                },
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("NEO notification delivery failed")
        return False
