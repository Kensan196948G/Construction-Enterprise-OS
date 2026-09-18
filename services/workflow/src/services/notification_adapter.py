"""WorkflowからNotification Serviceへ通知を渡す内部adapter。"""

import logging
from collections.abc import Iterable
from uuid import UUID

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


async def resolve_notification_recipients(
    *, organization_id: UUID, roles: Iterable[str], fallback: UUID | None = None
) -> list[UUID]:
    """Authから組織内の有効な受信者を取得する。失敗時は明示的なfallbackだけ返す。"""
    settings = get_settings()
    role_names = sorted({role for role in roles if role})
    if settings.AUTH_SERVICE_URL and settings.AUTH_INTERNAL_API_KEY and role_names:
        url = f"{settings.AUTH_SERVICE_URL.rstrip('/')}/api/v1/internal/recipients"
        try:
            async with httpx.AsyncClient(
                timeout=settings.NOTIFICATION_TIMEOUT_SECONDS
            ) as client:
                response = await client.get(
                    url,
                    params={
                        "organization_id": str(organization_id),
                        "roles": ",".join(role_names),
                    },
                    headers={"X-Internal-API-Key": settings.AUTH_INTERNAL_API_KEY},
                )
                response.raise_for_status()
                ids = [UUID(item["id"]) for item in response.json().get("data", [])]
                if ids:
                    return ids
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            logger.exception("Workflow notification recipient resolution failed: %s", url)
    return [fallback] if fallback else []


async def send_workflow_notification(
    *,
    recipient_id: UUID,
    template_code: str,
    instance_id: UUID,
    transition: str,
    actor_id: UUID,
    template_vars: dict,
    metadata: dict | None = None,
) -> bool:
    """Send a notification after the workflow transaction has completed.

    An unavailable or unconfigured Notification Service must not fail the already
    committed workflow transition. The receiver enforces the idempotency key.
    """
    settings = get_settings()
    if (
        not settings.NOTIFICATION_SERVICE_URL
        or not settings.NOTIFICATION_INTERNAL_API_KEY
    ):
        return False

    return await _send_notification(
        recipient_id=recipient_id,
        template_code=template_code,
        instance_id=instance_id,
        transition=transition,
        actor_id=actor_id,
        template_vars=template_vars,
        metadata=metadata,
    )


async def send_workflow_notifications(
    *,
    recipient_ids: Iterable[UUID],
    template_code: str,
    instance_id: UUID,
    transition: str,
    actor_id: UUID,
    template_vars: dict,
    metadata: dict | None = None,
) -> int:
    delivered = 0
    for recipient_id in dict.fromkeys(recipient_ids):
        if await _send_notification(
            recipient_id=recipient_id,
            template_code=template_code,
            instance_id=instance_id,
            transition=transition,
            actor_id=actor_id,
            template_vars=template_vars,
            metadata=metadata,
        ):
            delivered += 1
    return delivered


async def _send_notification(
    *,
    recipient_id: UUID,
    template_code: str,
    instance_id: UUID,
    transition: str,
    actor_id: UUID,
    template_vars: dict,
    metadata: dict | None = None,
) -> bool:
    settings = get_settings()
    if (
        not settings.NOTIFICATION_SERVICE_URL
        or not settings.NOTIFICATION_INTERNAL_API_KEY
    ):
        return False

    payload = {
        "recipient_id": str(recipient_id),
        "template_code": template_code,
        "template_vars": template_vars,
        "metadata": {
            "source": "workflow",
            "workflow_instance_id": str(instance_id),
            "transition": transition,
            **(metadata or {}),
        },
        "idempotency_key": f"workflow:{instance_id}:{transition}:{actor_id}:{recipient_id}",
    }
    url = f"{settings.NOTIFICATION_SERVICE_URL.rstrip('/')}/api/v1/notifications/send"
    try:
        async with httpx.AsyncClient(
            timeout=settings.NOTIFICATION_TIMEOUT_SECONDS
        ) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"X-Internal-API-Key": settings.NOTIFICATION_INTERNAL_API_KEY},
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Workflow notification delivery failed: %s", url)
        return False
