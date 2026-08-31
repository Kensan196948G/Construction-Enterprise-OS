"""システムヘルスチェックエンドポイント"""

from datetime import datetime, timezone
import asyncio
from typing import Literal

from fastapi import APIRouter
import httpx
from pydantic import BaseModel

from ..config import get_settings

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
    """設定済みサービスの実HTTPヘルス状態を返す。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    settings = get_settings()

    async def probe(name: str, url: str) -> ServiceHealth:
        try:
            async with httpx.AsyncClient(timeout=settings.HEALTH_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
            body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            service_status = body.get("status")
            if service_status not in {"healthy", "degraded", "unhealthy"}:
                service_status = "healthy" if response.is_success else "unhealthy"
            return ServiceHealth(
                name=name,
                status=service_status,
                latency_ms=0,
                version=str(body.get("version", "unknown")),
            )
        except (httpx.HTTPError, ValueError):
            return ServiceHealth(
                name=name, status="unhealthy", latency_ms=0, version="unknown"
            )

    services = [
        ServiceHealth(name="auth", status="healthy", latency_ms=0, version="0.1.0")
    ]
    services.extend(
        await asyncio.gather(
            *(probe(name, url) for name, url in settings.HEALTH_SERVICE_URLS.items())
        )
    )
    statuses = {service.status for service in services}
    overall: Literal["healthy", "degraded", "unhealthy"] = "unhealthy" if "unhealthy" in statuses else (
        "degraded" if "degraded" in statuses else "healthy"
    )

    return ServicesHealthResponse(
        services=services,
        overall=overall,
        checked_at=now,
    )
