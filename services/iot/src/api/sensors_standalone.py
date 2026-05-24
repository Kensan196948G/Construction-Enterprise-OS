"""環境センサー独立 API — stub（デバイス非依存）"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class SensorHistory(BaseModel):
    time: str
    value: float


class EnvSensor(BaseModel):
    id: str
    name: str
    location: str
    current_value: float
    unit: str
    normal_min: float
    normal_max: float
    state: str
    last_updated: str
    history: list[SensorHistory]


_MOCK_SENSORS = [
    EnvSensor(
        id="s1",
        name="温度センサー #1",
        location="第1工区 東側",
        current_value=28.5,
        unit="℃",
        normal_min=5.0,
        normal_max=35.0,
        state="normal",
        last_updated="2024-05-24T08:30:00",
        history=[
            SensorHistory(time="08:00", value=25.1),
            SensorHistory(time="08:15", value=26.3),
            SensorHistory(time="08:30", value=28.5),
        ],
    ),
    EnvSensor(
        id="s2",
        name="湿度センサー #1",
        location="第1工区 東側",
        current_value=72.0,
        unit="%",
        normal_min=30.0,
        normal_max=80.0,
        state="normal",
        last_updated="2024-05-24T08:30:00",
        history=[
            SensorHistory(time="08:00", value=68.5),
            SensorHistory(time="08:15", value=70.2),
            SensorHistory(time="08:30", value=72.0),
        ],
    ),
    EnvSensor(
        id="s3",
        name="粉塵センサー #1",
        location="第2工区",
        current_value=0.085,
        unit="mg/m³",
        normal_min=0.0,
        normal_max=0.1,
        state="warning",
        last_updated="2024-05-24T08:29:00",
        history=[
            SensorHistory(time="08:00", value=0.040),
            SensorHistory(time="08:15", value=0.065),
            SensorHistory(time="08:29", value=0.085),
        ],
    ),
    EnvSensor(
        id="s4",
        name="騒音センサー #1",
        location="現場境界",
        current_value=68.2,
        unit="dB",
        normal_min=0.0,
        normal_max=70.0,
        state="normal",
        last_updated="2024-05-24T08:30:00",
        history=[
            SensorHistory(time="08:00", value=55.0),
            SensorHistory(time="08:15", value=62.5),
            SensorHistory(time="08:30", value=68.2),
        ],
    ),
]


@router.get("/sensors")
async def list_sensors(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_SENSORS[start : start + per_page]
    return {"items": [s.model_dump() for s in items], "total": len(_MOCK_SENSORS)}
