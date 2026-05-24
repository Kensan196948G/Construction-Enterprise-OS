"""自律施工アクティビティログエンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import ActivityListResponse, ActivityResponse, APIResponse

router = APIRouter()

MOCK_ACTIVITIES = [
    ActivityResponse(
        id="act1",
        time="2026-05-24T09:15:00",
        activity_type="success",
        message="AE-001 掘削作業 第3工区 完了",
        severity=None,
    ),
    ActivityResponse(
        id="act2",
        time="2026-05-24T09:10:00",
        activity_type="info",
        message="DR-007 資材運搬タスク開始 — 鉄骨材 D区画→倉庫",
        severity="info",
    ),
    ActivityResponse(
        id="act3",
        time="2026-05-24T09:05:00",
        activity_type="warning",
        message="SEN-003 振動センサー警告値超過 (12.8 mm/s)",
        severity="warning",
    ),
    ActivityResponse(
        id="act4",
        time="2026-05-24T09:00:00",
        activity_type="info",
        message="デジタルツイン twin-001 同期完了",
        severity="info",
    ),
    ActivityResponse(
        id="act5",
        time="2026-05-24T08:55:00",
        activity_type="warning",
        message="AE-003 バッテリー残量低下 (45.2%)",
        severity="warning",
    ),
    ActivityResponse(
        id="act6",
        time="2026-05-24T08:50:00",
        activity_type="error",
        message="RPAタスク「安全巡回チェックリスト配信」実行失敗",
        severity="critical",
    ),
    ActivityResponse(
        id="act7",
        time="2026-05-24T08:45:00",
        activity_type="success",
        message="FL-004 ドローン飛行 D工区南エリア 完了 — カバレッジ 88.4%",
        severity=None,
    ),
    ActivityResponse(
        id="act8",
        time="2026-05-24T08:30:00",
        activity_type="info",
        message="AC-002 スタンバイ状態へ移行",
        severity="info",
    ),
    ActivityResponse(
        id="act9",
        time="2026-05-24T08:15:00",
        activity_type="success",
        message="RPA「資材発注書自動生成」実行完了 (2.5分)",
        severity=None,
    ),
    ActivityResponse(
        id="act10",
        time="2026-05-24T07:00:00",
        activity_type="info",
        message="CB-001 定期メンテナンス開始",
        severity="info",
    ),
]


@router.get("", response_model=APIResponse[ActivityListResponse])
async def list_activities(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    activity_type: str | None = Query(None),
):
    items = MOCK_ACTIVITIES
    if activity_type:
        items = [a for a in items if a.activity_type == activity_type]
    start = (page - 1) * per_page
    return APIResponse(
        data=ActivityListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
