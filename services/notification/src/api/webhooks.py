"""Webhook管理エンドポイント"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

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
