"""NEO callbackをWorkflow監査ログへ反映するadapter。"""

import logging

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


async def reflect_neo_callback(notification, payload) -> bool | None:
    settings = get_settings()
    metadata = notification.metadata_ or {}
    workflow_instance_id = metadata.get("workflow_instance_id")
    if not settings.WORKFLOW_SERVICE_URL or not settings.WORKFLOW_INTERNAL_JOB_API_KEY:
        return None
    if not workflow_instance_id:
        return None
    url = (
        f"{settings.WORKFLOW_SERVICE_URL.rstrip('/')}/api/v1/workflow/"
        "internal/notification-callback"
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json={
                    "workflow_instance_id": workflow_instance_id,
                    "notification_id": notification.id,
                    "idempotency_key": payload.idempotency_key,
                    "event": payload.event,
                    "response": payload.response,
                    "occurred_at": payload.occurred_at.isoformat()
                    if payload.occurred_at
                    else None,
                },
                headers={
                    "X-Internal-API-Key": settings.WORKFLOW_INTERNAL_JOB_API_KEY
                },
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Workflow notification callback reflection failed")
        return False
