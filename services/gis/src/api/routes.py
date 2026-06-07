"""輸送ルート管理 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class TransportRoute(BaseModel):
    id: str
    name: str
    origin: str
    destination: str
    distance: float
    duration: int
    weight_limit: float
    status: str
    trips_this_month: int


_MOCK_ROUTES = [
    TransportRoute(
        id="r1",
        name="メインルート A",
        origin="資材置き場",
        destination="第1工区",
        distance=1.2,
        duration=8,
        weight_limit=20.0,
        status="通常",
        trips_this_month=45,
    ),
    TransportRoute(
        id="r2",
        name="搬入ルート B",
        origin="搬入口",
        destination="第2工区",
        distance=0.8,
        duration=5,
        weight_limit=15.0,
        status="工事中",
        trips_this_month=23,
    ),
    TransportRoute(
        id="r3",
        name="重機搬送ルート C",
        origin="機材置き場",
        destination="第3工区",
        distance=1.5,
        duration=12,
        weight_limit=50.0,
        status="通常",
        trips_this_month=12,
    ),
    TransportRoute(
        id="r4",
        name="廃材搬出ルート D",
        origin="第1工区",
        destination="廃材仮置き場",
        distance=0.6,
        duration=4,
        weight_limit=10.0,
        status="迂回推奨",
        trips_this_month=67,
    ),
    TransportRoute(
        id="r5",
        name="緊急搬入ルート E",
        origin="正門",
        destination="全工区",
        distance=2.0,
        duration=15,
        weight_limit=30.0,
        status="通行止め",
        trips_this_month=0,
    ),
]


@router.get("")
async def list_routes(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_ROUTES[start : start + per_page]
    return {
        "data": {"items": [r.model_dump() for r in items], "total": len(_MOCK_ROUTES)}
    }
