"""ドローン飛行記録管理エンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import APIResponse, DroneFlightListResponse, DroneFlightResponse

router = APIRouter()

MOCK_DRONE_FLIGHTS = [
    DroneFlightResponse(
        id="df1",
        flight_id="FL-001",
        date="2026-05-20",
        pilot="田中 一郎",
        area="A工区 全体",
        altitude=120.0,
        flight_time_min=65,
        photo_count=380,
        status="completed",
        coverage=97.5,
    ),
    DroneFlightResponse(
        id="df2",
        flight_id="FL-002",
        date="2026-05-21",
        pilot="佐藤 二郎",
        area="B工区 北エリア",
        altitude=100.0,
        flight_time_min=45,
        photo_count=210,
        status="completed",
        coverage=91.2,
    ),
    DroneFlightResponse(
        id="df3",
        flight_id="FL-003",
        date="2026-05-22",
        pilot="鈴木 三郎",
        area="C工区 基礎部",
        altitude=150.0,
        flight_time_min=90,
        photo_count=500,
        status="completed",
        coverage=99.0,
    ),
    DroneFlightResponse(
        id="df4",
        flight_id="FL-004",
        date="2026-05-23",
        pilot="田中 一郎",
        area="D工区 南エリア",
        altitude=130.0,
        flight_time_min=55,
        photo_count=295,
        status="completed",
        coverage=88.4,
    ),
    DroneFlightResponse(
        id="df5",
        flight_id="FL-005",
        date="2026-05-24",
        pilot="高橋 四郎",
        area="E工区 全体",
        altitude=110.0,
        flight_time_min=70,
        photo_count=420,
        status="in_progress",
        coverage=62.0,
    ),
    DroneFlightResponse(
        id="df6",
        flight_id="FL-006",
        date="2026-05-25",
        pilot="佐藤 二郎",
        area="F工区 西エリア",
        altitude=125.0,
        flight_time_min=80,
        photo_count=0,
        status="planned",
        coverage=0.0,
    ),
]


@router.get("", response_model=APIResponse[DroneFlightListResponse])
async def list_drone_flights(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
):
    items = MOCK_DRONE_FLIGHTS
    if status:
        items = [f for f in items if f.status == status]
    start = (page - 1) * per_page
    return APIResponse(
        data=DroneFlightListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
