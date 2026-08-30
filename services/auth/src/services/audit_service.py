"""監査ログ検索ビジネスロジック"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuditLog


async def get_audit_logs_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    event_type: str | None = None,
    user_id: uuid.UUID | None = None,
    success: bool | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> tuple[list[AuditLog], int]:
    conditions = []
    if event_type:
        conditions.append(AuditLog.event_type == event_type)
    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if success is not None:
        conditions.append(AuditLog.success == success)
    if since:
        conditions.append(AuditLog.created_at >= since)
    if until:
        conditions.append(AuditLog.created_at <= until)

    base_query = select(AuditLog)
    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count()).select_from(AuditLog)
    if conditions:
        count_query = count_query.where(*conditions)
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        base_query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    logs = list((await db.execute(query)).scalars().all())
    return logs, total
