"""RPAタスク管理エンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import APIResponse, RpaTaskListResponse, RpaTaskResponse

router = APIRouter()

MOCK_RPA_TASKS = [
    RpaTaskResponse(
        id="rpa1",
        name="日報自動集計・送信",
        trigger="schedule",
        schedule="毎日 18:00",
        last_result="success",
        last_run="2026-05-24T18:00:05",
        avg_duration_min=3.5,
        runs_this_month=24,
        is_active=True,
    ),
    RpaTaskResponse(
        id="rpa2",
        name="資材発注書自動生成",
        trigger="event",
        schedule=None,
        last_result="success",
        last_run="2026-05-24T08:15:32",
        avg_duration_min=2.5,
        runs_this_month=12,
        is_active=True,
    ),
    RpaTaskResponse(
        id="rpa3",
        name="週次進捗レポート作成",
        trigger="schedule",
        schedule="毎週月曜 09:00",
        last_result="success",
        last_run="2026-05-20T09:00:12",
        avg_duration_min=8.0,
        runs_this_month=4,
        is_active=True,
    ),
    RpaTaskResponse(
        id="rpa4",
        name="安全巡回チェックリスト配信",
        trigger="schedule",
        schedule="毎日 07:30",
        last_result="failed",
        last_run="2026-05-24T07:30:08",
        avg_duration_min=1.5,
        runs_this_month=24,
        is_active=True,
    ),
    RpaTaskResponse(
        id="rpa5",
        name="工程表自動更新",
        trigger="event",
        schedule=None,
        last_result="running",
        last_run="2026-05-24T09:20:00",
        avg_duration_min=15.0,
        runs_this_month=8,
        is_active=True,
    ),
    RpaTaskResponse(
        id="rpa6",
        name="月次原価精算バッチ",
        trigger="schedule",
        schedule="毎月1日 02:00",
        last_result="success",
        last_run="2026-05-01T02:01:45",
        avg_duration_min=12.0,
        runs_this_month=1,
        is_active=False,
    ),
]


@router.get("", response_model=APIResponse[RpaTaskListResponse])
async def list_rpa_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: bool | None = Query(None),
):
    items = MOCK_RPA_TASKS
    if is_active is not None:
        items = [t for t in items if t.is_active == is_active]
    start = (page - 1) * per_page
    return APIResponse(
        data=RpaTaskListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
