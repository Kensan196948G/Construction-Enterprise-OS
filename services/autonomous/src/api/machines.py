"""自律施工機械管理エンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import APIResponse, MachineListResponse, MachineResponse

router = APIRouter()

MOCK_MACHINES = [
    MachineResponse(
        id="m1",
        machine_no="AE-001",
        machine_type="autonomous_excavator",
        status="working",
        location="A区画",
        battery_level=72.5,
        current_task="掘削作業 第3工区",
        last_updated="2026-05-24T09:00:00",
    ),
    MachineResponse(
        id="m2",
        machine_no="AC-002",
        machine_type="autonomous_crane",
        status="standby",
        location="B区画",
        battery_level=91.0,
        current_task=None,
        last_updated="2026-05-24T08:30:00",
    ),
    MachineResponse(
        id="m3",
        machine_no="AE-003",
        machine_type="autonomous_excavator",
        status="working",
        location="C区画",
        battery_level=45.2,
        current_task="基礎掘削 南エリア",
        last_updated="2026-05-24T09:15:00",
    ),
    MachineResponse(
        id="m4",
        machine_no="CB-001",
        machine_type="crawler_bulldozer",
        status="maintenance",
        location="整備エリア",
        battery_level=100.0,
        current_task=None,
        last_updated="2026-05-24T07:00:00",
    ),
    MachineResponse(
        id="m5",
        machine_no="DR-007",
        machine_type="delivery_robot",
        status="working",
        location="D区画→倉庫",
        battery_level=58.0,
        current_task="資材運搬 鉄骨材",
        last_updated="2026-05-24T09:10:00",
    ),
    MachineResponse(
        id="m6",
        machine_no="AC-004",
        machine_type="autonomous_compactor",
        status="working",
        location="E区画",
        battery_level=83.0,
        current_task="地盤締固め",
        last_updated="2026-05-24T09:05:00",
    ),
]


@router.get("", response_model=APIResponse[MachineListResponse])
async def list_machines(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
):
    items = MOCK_MACHINES
    if status:
        items = [m for m in items if m.status == status]
    start = (page - 1) * per_page
    return APIResponse(
        data=MachineListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
