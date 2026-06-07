"""建設機械管理 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class Machine(BaseModel):
    id: str
    machine_number: str
    type: str
    location: str
    status: str
    engine_hours: float
    fuel_level: float
    gps_lat: float | None = None
    gps_lng: float | None = None
    last_comm: str


_MOCK_MACHINES = [
    Machine(
        id="m1",
        machine_number="EX-001",
        type="油圧ショベル",
        location="第1工区",
        status="稼働中",
        engine_hours=1234.5,
        fuel_level=75.0,
        gps_lat=35.6812,
        gps_lng=139.7671,
        last_comm="2024-05-24T08:30:00",
    ),
    Machine(
        id="m2",
        machine_number="BL-002",
        type="ブルドーザー",
        location="第2工区",
        status="稼働中",
        engine_hours=876.2,
        fuel_level=60.5,
        gps_lat=35.6815,
        gps_lng=139.7675,
        last_comm="2024-05-24T08:28:00",
    ),
    Machine(
        id="m3",
        machine_number="CR-003",
        type="クレーン",
        location="第3工区",
        status="点検中",
        engine_hours=2341.0,
        fuel_level=45.0,
        gps_lat=35.6820,
        gps_lng=139.7680,
        last_comm="2024-05-24T07:00:00",
    ),
    Machine(
        id="m4",
        machine_number="DP-004",
        type="ダンプトラック",
        location="搬入口",
        status="待機中",
        engine_hours=567.8,
        fuel_level=90.0,
        gps_lat=35.6808,
        gps_lng=139.7665,
        last_comm="2024-05-24T08:25:00",
    ),
    Machine(
        id="m5",
        machine_number="RO-005",
        type="振動ローラー",
        location="仮設工区",
        status="停止",
        engine_hours=432.1,
        fuel_level=30.0,
        gps_lat=None,
        gps_lng=None,
        last_comm="2024-05-23T17:00:00",
    ),
]


@router.get("/machines")
async def list_machines(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_MACHINES[start : start + per_page]
    return {"items": [m.model_dump() for m in items], "total": len(_MOCK_MACHINES)}
