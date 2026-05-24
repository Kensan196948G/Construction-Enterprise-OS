"""テレメトリデータサービス"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import Telemetry as TelemetryModel
from ..schemas import TelemetryPoint


async def ingest_telemetry(db: AsyncSession, data: list[TelemetryPoint]) -> int:
    """バルク挿入。アラートチェックのために挿入したメトリクスを返す。"""
    if not data:
        return 0

    now = datetime.now(timezone.utc)
    bulk_args = []
    for point in data:
        ts = point.timestamp if point.timestamp else now
        bulk_args.append(
            {
                "device_id": point.device_id,
                "sensor_id": point.sensor_id,
                "metric_name": point.metric_name,
                "value": point.value,
                "unit": point.unit,
                "timestamp": ts,
                "metadata": point.metadata or {},
            }
        )

    settings = get_settings()
    batch_size = settings.TELEMETRY_BATCH_SIZE
    total = 0
    for i in range(0, len(bulk_args), batch_size):
        batch = bulk_args[i : i + batch_size]
        stmt = TelemetryModel.__table__.insert().values(batch)  # type: ignore[attr-defined]
        await db.execute(stmt)
        total += len(batch)

    return total


async def query_telemetry(
    db: AsyncSession,
    device_id: UUID,
    start_time: datetime,
    end_time: datetime,
    metric_name: str | None = None,
    limit: int = 100,
) -> list[TelemetryModel]:
    query = select(TelemetryModel).where(
        TelemetryModel.device_id == device_id,
        TelemetryModel.timestamp >= start_time,
        TelemetryModel.timestamp <= end_time,
    )
    if metric_name:
        query = query.where(TelemetryModel.metric_name == metric_name)

    query = query.order_by(TelemetryModel.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_latest_telemetry(db: AsyncSession, device_id: UUID) -> list[dict]:
    query = text("""
        SELECT DISTINCT ON (metric_name)
            sensor_id, metric_name, value, unit, timestamp
        FROM iot.telemetry
        WHERE device_id = :device_id
        ORDER BY metric_name, timestamp DESC
    """)
    result = await db.execute(query, {"device_id": device_id})
    rows = result.fetchall()
    return [
        {
            "sensor_id": row.sensor_id,
            "metric_name": row.metric_name,
            "value": row.value,
            "unit": row.unit,
            "timestamp": row.timestamp,
        }
        for row in rows
    ]
