"""Webhook管理とNEO callbackエンドポイント"""

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import Notification
from ..models.base import get_db
from ..services.workflow_callback import reflect_neo_callback

router = APIRouter()


class WebhookResponse(BaseModel):
    id: str
    name: str
    url: str
    events: list[str]
    auth_type: str
    last_fired: str | None = None
    success_rate: float
    status: str


class WebhookListResponse(BaseModel):
    items: list[WebhookResponse]
    total: int


class NeoNotificationCallback(BaseModel):
    notification_id: int
    idempotency_key: str
    event: Literal["opened", "read", "responded", "acknowledged"]
    response: str | None = None
    occurred_at: datetime | None = None


MOCK_WEBHOOKS = [
    WebhookResponse(
        id="wh1",
        name="CI/CD Pipeline通知",
        url="https://hooks.example.com/cicd/abc123",
        events=["build.success", "build.failure", "deploy.success"],
        auth_type="bearer",
        last_fired="2026-05-24T08:30:00",
        success_rate=98.5,
        status="active",
    ),
    WebhookResponse(
        id="wh2",
        name="Slack工事進捗通知",
        url="https://hooks.slack.com/services/T000/B000/xxx",
        events=["project.status_changed", "issue.critical"],
        auth_type="none",
        last_fired="2026-05-24T07:15:00",
        success_rate=100.0,
        status="active",
    ),
    WebhookResponse(
        id="wh3",
        name="外部ERPシステム連携",
        url="https://erp.client.co.jp/api/webhook/constr",
        events=["invoice.created", "payment.received"],
        auth_type="hmac",
        last_fired="2026-05-23T16:00:00",
        success_rate=87.3,
        status="active",
    ),
    WebhookResponse(
        id="wh4",
        name="安全管理システム連携",
        url="https://safety.example.com/hooks/events",
        events=["safety.incident", "inspection.failed"],
        auth_type="bearer",
        last_fired="2026-05-22T11:30:00",
        success_rate=95.0,
        status="inactive",
    ),
    WebhookResponse(
        id="wh5",
        name="BIMデータ同期",
        url="https://bim.partner.com/sync/webhook",
        events=["document.uploaded", "bim.model_updated"],
        auth_type="basic",
        last_fired="2026-05-24T06:00:00",
        success_rate=92.1,
        status="active",
    ),
]


@router.post("/neo/callback")
async def neo_callback(
    request: Request,
    payload: NeoNotificationCallback,
    x_neo_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """NEOの開封・応答結果を署名検証して通知レコードへ反映する。"""
    secret = get_settings().NEO_WEBHOOK_SECRET
    body = await request.body()
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not secret or not x_neo_signature or not hmac.compare_digest(
        x_neo_signature, expected
    ):
        raise HTTPException(status_code=403, detail="NEO callback authentication required")

    result = await db.execute(
        select(Notification).where(
            Notification.id == payload.notification_id,
            Notification.idempotency_key == payload.idempotency_key,
        )
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    metadata = dict(notification.metadata_ or {})
    metadata["neo_callback"] = {
        "event": payload.event,
        "response": payload.response,
        "occurred_at": (payload.occurred_at or datetime.now(timezone.utc)).isoformat(),
    }
    notification.metadata_ = metadata
    if payload.event in {"opened", "read", "responded", "acknowledged"}:
        notification.status = "read"
        notification.read_at = payload.occurred_at or datetime.now(timezone.utc)
    workflow_reflected = await reflect_neo_callback(notification, payload)
    if workflow_reflected is False:
        raise HTTPException(status_code=502, detail="Workflow callback unavailable")
    await db.flush()
    return {
        "success": True,
        "notification_id": notification.id,
        "workflow_reflected": workflow_reflected,
    }


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
):
    items = MOCK_WEBHOOKS
    if status:
        items = [w for w in items if w.status == status]
    start = (page - 1) * per_page
    return WebhookListResponse(items=items[start : start + per_page], total=len(items))
