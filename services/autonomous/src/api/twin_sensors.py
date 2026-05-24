"""デジタルツインセンサー管理エンドポイント"""

from fastapi import APIRouter, Query
from ..schemas import APIResponse, TwinSensorListResponse, TwinSensorResponse

router = APIRouter()

MOCK_TWIN_SENSORS = [
    TwinSensorResponse(
        id="sen1",
        sensor_id="SEN-001",
        twin_id="twin-001",
        sensor_type="temperature",
        location="A工区 基礎部",
        value=28.5,
        unit="°C",
        status="normal",
        last_updated="2026-05-24T09:00:00",
    ),
    TwinSensorResponse(
        id="sen2",
        sensor_id="SEN-002",
        twin_id="twin-001",
        sensor_type="humidity",
        location="A工区 基礎部",
        value=62.3,
        unit="%",
        status="normal",
        last_updated="2026-05-24T09:00:00",
    ),
    TwinSensorResponse(
        id="sen3",
        sensor_id="SEN-003",
        twin_id="twin-002",
        sensor_type="vibration",
        location="B工区 杭打ち現場",
        value=12.8,
        unit="mm/s",
        status="warning",
        last_updated="2026-05-24T09:05:00",
    ),
    TwinSensorResponse(
        id="sen4",
        sensor_id="SEN-004",
        twin_id="twin-002",
        sensor_type="pressure",
        location="B工区 地盤",
        value=2.45,
        unit="MPa",
        status="normal",
        last_updated="2026-05-24T09:05:00",
    ),
    TwinSensorResponse(
        id="sen5",
        sensor_id="SEN-005",
        twin_id="twin-003",
        sensor_type="temperature",
        location="C工区 コンクリート養生",
        value=35.2,
        unit="°C",
        status="warning",
        last_updated="2026-05-24T08:55:00",
    ),
    TwinSensorResponse(
        id="sen6",
        sensor_id="SEN-006",
        twin_id="twin-003",
        sensor_type="vibration",
        location="C工区 構造体",
        value=25.6,
        unit="mm/s",
        status="critical",
        last_updated="2026-05-24T09:10:00",
    ),
    TwinSensorResponse(
        id="sen7",
        sensor_id="SEN-007",
        twin_id="twin-004",
        sensor_type="humidity",
        location="D工区 トンネル内",
        value=88.1,
        unit="%",
        status="warning",
        last_updated="2026-05-24T09:00:00",
    ),
    TwinSensorResponse(
        id="sen8",
        sensor_id="SEN-008",
        twin_id="twin-004",
        sensor_type="pressure",
        location="D工区 支保工",
        value=1.82,
        unit="MPa",
        status="normal",
        last_updated="2026-05-24T09:00:00",
    ),
]


@router.get("", response_model=APIResponse[TwinSensorListResponse])
async def list_twin_sensors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sensor_type: str | None = Query(None),
    status: str | None = Query(None),
    twin_id: str | None = Query(None),
):
    items = MOCK_TWIN_SENSORS
    if sensor_type:
        items = [s for s in items if s.sensor_type == sensor_type]
    if status:
        items = [s for s in items if s.status == status]
    if twin_id:
        items = [s for s in items if s.twin_id == twin_id]
    start = (page - 1) * per_page
    return APIResponse(
        data=TwinSensorListResponse(
            items=items[start : start + per_page], total=len(items)
        )
    )
