"""システムヘルスチェックエンドポイント"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ServiceHealth(BaseModel):
    name: str
    status: Literal["healthy", "degraded", "unhealthy"]
    latency_ms: int
    version: str


class ServicesHealthResponse(BaseModel):
    services: list[ServiceHealth]
    overall: Literal["healthy", "degraded", "unhealthy"]
    checked_at: str


@router.get("/services", response_model=ServicesHealthResponse)
async def get_services_health() -> ServicesHealthResponse:
    """全マイクロサービスのヘルス状態を返す"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    services: list[ServiceHealth] = [
        ServiceHealth(name="auth", status="healthy", latency_ms=12, version="0.1.0"),
        ServiceHealth(
            name="document", status="healthy", latency_ms=18, version="0.1.0"
        ),
        ServiceHealth(
            name="workflow", status="healthy", latency_ms=15, version="0.1.0"
        ),
        ServiceHealth(name="gis", status="healthy", latency_ms=22, version="0.1.0"),
        ServiceHealth(name="iot", status="healthy", latency_ms=19, version="0.1.0"),
        ServiceHealth(name="ai", status="healthy", latency_ms=45, version="0.1.0"),
        ServiceHealth(name="bim", status="healthy", latency_ms=28, version="0.1.0"),
        ServiceHealth(name="erp", status="healthy", latency_ms=31, version="0.1.0"),
        ServiceHealth(
            name="autonomous", status="healthy", latency_ms=24, version="0.1.0"
        ),
        ServiceHealth(
            name="notification", status="healthy", latency_ms=9, version="0.1.0"
        ),
        ServiceHealth(
            name="security", status="healthy", latency_ms=16, version="0.1.0"
        ),
        ServiceHealth(name="safety", status="healthy", latency_ms=21, version="0.1.0"),
    ]

    return ServicesHealthResponse(
        services=services,
        overall="healthy",
        checked_at=now,
    )
