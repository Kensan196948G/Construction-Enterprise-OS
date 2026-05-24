"""テレメトリデータ投入・クエリエンドポイント"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import get_current_client, get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    LatestTelemetryValue,
    TelemetryIngestRequest,
)
from ..services.telemetry_service import ingest_telemetry, query_telemetry, get_latest_telemetry
from ..services.alert_service import check_alert_rules

router = APIRouter()


@router.post("/ingest", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest(
    request: Request,
    body: TelemetryIngestRequest,
    db: AsyncSession = Depends(get_db),
    _current_client=Depends(get_current_client),
):
    count = await ingest_telemetry(db, body.data)

    for point in body.data:
        await check_alert_rules(
            db,
            device_id=point.device_id,
            metric_name=point.metric_name,
            value=point.value,
            sensor_id=point.sensor_id,
        )

    return APIResponse(data={"ingested": count, "message": f"{count}件のテレメトリデータを投入しました。"})


@router.get("/{device_id}", response_model=APIResponse)
async def query_device_telemetry(
    request: Request,
    device_id: UUID,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    metric_name: str | None = Query(None),
    limit: int = Query(100, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    rows = await query_telemetry(
        db,
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        metric_name=metric_name,
        limit=limit,
    )
    return APIResponse(data=[
        {
            "id": r.id,
            "device_id": str(r.device_id),
            "sensor_id": str(r.sensor_id) if r.sensor_id else None,
            "metric_name": r.metric_name,
            "value": r.value,
            "unit": r.unit,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ])


@router.get("/{device_id}/latest", response_model=APIResponse[list[LatestTelemetryValue]])
async def latest_telemetry(
    request: Request,
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    rows = await get_latest_telemetry(db, device_id)
    return APIResponse(data=[LatestTelemetryValue(**r) for r in rows])
