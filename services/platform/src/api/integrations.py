"""システム連携（インテグレーション）管理エンドポイント"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class IntegrationSystemResponse(BaseModel):
    id: str
    name: str
    system_type: str
    status: str
    last_sync: str | None = None
    sync_interval_min: int
    records_synced: int
    error_count: int


class IntegrationLogResponse(BaseModel):
    id: str
    system_id: str
    system_name: str
    event_type: str
    status: str
    records: int
    duration_ms: int
    message: str | None = None
    occurred_at: str


class IntegrationListResponse(BaseModel):
    items: list[IntegrationSystemResponse]
    total: int


class IntegrationLogListResponse(BaseModel):
    items: list[IntegrationLogResponse]
    total: int


MOCK_SYSTEMS = [
    IntegrationSystemResponse(
        id="i1",
        name="SAP ERP連携",
        system_type="erp",
        status="active",
        last_sync="2026-05-24T09:00:00",
        sync_interval_min=60,
        records_synced=15234,
        error_count=0,
    ),
    IntegrationSystemResponse(
        id="i2",
        name="Autodesk BIM 360",
        system_type="bim",
        status="active",
        last_sync="2026-05-24T08:30:00",
        sync_interval_min=30,
        records_synced=428,
        error_count=2,
    ),
    IntegrationSystemResponse(
        id="i3",
        name="Salesforce CRM",
        system_type="crm",
        status="active",
        last_sync="2026-05-24T09:15:00",
        sync_interval_min=120,
        records_synced=3891,
        error_count=0,
    ),
    IntegrationSystemResponse(
        id="i4",
        name="Slack通知連携",
        system_type="messaging",
        status="active",
        last_sync="2026-05-24T09:20:00",
        sync_interval_min=5,
        records_synced=892,
        error_count=1,
    ),
    IntegrationSystemResponse(
        id="i5",
        name="Box クラウドストレージ",
        system_type="storage",
        status="warning",
        last_sync="2026-05-23T22:00:00",
        sync_interval_min=240,
        records_synced=12567,
        error_count=5,
    ),
    IntegrationSystemResponse(
        id="i6",
        name="勤怠管理システム",
        system_type="hr",
        status="active",
        last_sync="2026-05-24T07:00:00",
        sync_interval_min=1440,
        records_synced=287,
        error_count=0,
    ),
]

MOCK_LOGS = [
    IntegrationLogResponse(
        id="l1",
        system_id="i1",
        system_name="SAP ERP連携",
        event_type="sync",
        status="success",
        records=245,
        duration_ms=1823,
        message=None,
        occurred_at="2026-05-24T09:00:00",
    ),
    IntegrationLogResponse(
        id="l2",
        system_id="i2",
        system_name="Autodesk BIM 360",
        event_type="sync",
        status="partial",
        records=12,
        duration_ms=3241,
        message="2件のモデル変換エラー",
        occurred_at="2026-05-24T08:30:00",
    ),
    IntegrationLogResponse(
        id="l3",
        system_id="i3",
        system_name="Salesforce CRM",
        event_type="sync",
        status="success",
        records=38,
        duration_ms=892,
        message=None,
        occurred_at="2026-05-24T09:15:00",
    ),
    IntegrationLogResponse(
        id="l4",
        system_id="i4",
        system_name="Slack通知連携",
        event_type="notification",
        status="success",
        records=5,
        duration_ms=124,
        message=None,
        occurred_at="2026-05-24T09:20:00",
    ),
    IntegrationLogResponse(
        id="l5",
        system_id="i5",
        system_name="Box クラウドストレージ",
        event_type="sync",
        status="failed",
        records=0,
        duration_ms=30000,
        message="タイムアウトエラー: 接続確立失敗",
        occurred_at="2026-05-23T22:00:00",
    ),
    IntegrationLogResponse(
        id="l6",
        system_id="i1",
        system_name="SAP ERP連携",
        event_type="sync",
        status="success",
        records=189,
        duration_ms=1654,
        message=None,
        occurred_at="2026-05-24T08:00:00",
    ),
]


@router.get("", response_model=IntegrationListResponse)
async def list_integrations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
):
    items = MOCK_SYSTEMS
    if status:
        items = [i for i in items if i.status == status]
    start = (page - 1) * per_page
    return IntegrationListResponse(
        items=items[start : start + per_page], total=len(items)
    )


@router.get("/logs", response_model=IntegrationLogListResponse)
async def list_integration_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    system_id: str | None = Query(None),
    status: str | None = Query(None),
):
    items = MOCK_LOGS
    if system_id:
        items = [l for l in items if l.system_id == system_id]
    if status:
        items = [l for l in items if l.status == status]
    start = (page - 1) * per_page
    return IntegrationLogListResponse(
        items=items[start : start + per_page], total=len(items)
    )
