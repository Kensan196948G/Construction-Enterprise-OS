"""システムヘルスチェックエンドポイント"""

from datetime import datetime, timezone
import asyncio
import time
from typing import Literal, cast

from fastapi import APIRouter, Depends
import httpx
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.base import get_db

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
async def get_services_health(
    db: AsyncSession = Depends(get_db),
) -> ServicesHealthResponse:
    """設定済みサービスの実HTTPヘルス状態と、自身のDB到達性を返す。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    settings = get_settings()

    async def probe(name: str, url: str) -> ServiceHealth:
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(
                timeout=settings.HEALTH_TIMEOUT_SECONDS
            ) as client:
                response = await client.get(url)
            payload = (
                response.json()
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else {}
            )
            body = payload if isinstance(payload, dict) else {}
            service_status: Literal["healthy", "degraded", "unhealthy"]
            if response.is_success:
                raw_status = body.get("status")
                if raw_status in ("healthy", "degraded", "unhealthy"):
                    service_status = cast(
                        Literal["healthy", "degraded", "unhealthy"], raw_status
                    )
                else:
                    service_status = "healthy"
            else:
                service_status = "unhealthy"
            return ServiceHealth(
                name=name,
                status=service_status,
                latency_ms=int((time.perf_counter() - started) * 1000),
                version=str(body.get("version", "unknown")),
            )
        except (httpx.HTTPError, ValueError):
            return ServiceHealth(
                name=name,
                status="unhealthy",
                latency_ms=int((time.perf_counter() - started) * 1000),
                version="unknown",
            )

    # auth 自身を無条件 healthy と自己申告すると、DB 障害時も overall が
    # healthy になり監視が機能しない。自分の DB で判定する。
    started = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        auth_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    except Exception:
        auth_status = "unhealthy"
    auth_latency = int((time.perf_counter() - started) * 1000)

    services = [
        ServiceHealth(
            name="auth",
            status=auth_status,
            latency_ms=auth_latency,
            version="0.1.0",
        )
    ]
    services.extend(
        await asyncio.gather(
            *(probe(name, url) for name, url in settings.HEALTH_SERVICE_URLS.items())
        )
    )
    statuses = {service.status for service in services}
    overall: Literal["healthy", "degraded", "unhealthy"] = (
        "unhealthy"
        if "unhealthy" in statuses
        else ("degraded" if "degraded" in statuses else "healthy")
    )

    return ServicesHealthResponse(
        services=services,
        overall=overall,
        checked_at=now,
    )
