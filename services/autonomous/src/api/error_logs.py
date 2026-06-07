"""自律施工エラーログ管理エンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import APIResponse, ErrorLogListResponse, ErrorLogResponse

router = APIRouter()

MOCK_ERROR_LOGS = [
    ErrorLogResponse(
        id="err1",
        machine_no="AE-003",
        error_code="E001",
        message="バッテリー残量低下警告 (45.2%) — 充電ステーションへの帰還を推奨",
        severity="warning",
        occurred_at="2026-05-24T08:55:00",
        resolved_at=None,
        status="open",
    ),
    ErrorLogResponse(
        id="err2",
        machine_no="CB-001",
        error_code="E002",
        message="油圧システム圧力異常検知 — 定期メンテナンスへ移行",
        severity="critical",
        occurred_at="2026-05-24T06:50:00",
        resolved_at="2026-05-24T07:05:00",
        status="resolved",
    ),
    ErrorLogResponse(
        id="err3",
        machine_no="AC-002",
        error_code="E003",
        message="GPS信号受信不良 — 自律動作を一時停止しスタンバイへ移行",
        severity="warning",
        occurred_at="2026-05-24T08:25:00",
        resolved_at="2026-05-24T08:32:00",
        status="resolved",
    ),
    ErrorLogResponse(
        id="err4",
        machine_no="DR-007",
        error_code="E004",
        message="障害物検知センサー誤作動 — ルート再計算実施",
        severity="warning",
        occurred_at="2026-05-24T09:08:00",
        resolved_at=None,
        status="open",
    ),
    ErrorLogResponse(
        id="err5",
        machine_no="AE-001",
        error_code="E005",
        message="掘削アーム動作範囲超過警告 — 自動補正完了",
        severity="warning",
        occurred_at="2026-05-24T08:58:00",
        resolved_at="2026-05-24T08:59:30",
        status="resolved",
    ),
]


@router.get("", response_model=APIResponse[ErrorLogListResponse])
async def list_error_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    machine_no: str | None = Query(None),
):
    items = MOCK_ERROR_LOGS
    if severity:
        items = [e for e in items if e.severity == severity]
    if status:
        items = [e for e in items if e.status == status]
    if machine_no:
        items = [e for e in items if e.machine_no == machine_no]
    start = (page - 1) * per_page
    return APIResponse(
        data=ErrorLogListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
