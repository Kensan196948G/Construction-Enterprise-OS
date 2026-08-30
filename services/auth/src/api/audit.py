"""監査ログエンドポイント"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    AuditLogListResponse,
    AuditLogResponse,
    MetaInfo,
    TokenData,
)
from ..services.audit_service import get_audit_logs_paginated

router = APIRouter()


@router.get("", response_model=APIResponse[AuditLogListResponse])
async def list_audit_logs(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    event_type: str | None = Query(None),
    user_id: UUID | None = Query(None),
    success: bool | None = Query(None),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(
        require_permission("audit", "read", admin_bypass=False)
    ),
):
    """監査ログ検索(フィルタ・ページネーション)"""
    logs, total = await get_audit_logs_paginated(
        db,
        page=page,
        per_page=per_page,
        event_type=event_type,
        user_id=user_id,
        success=success,
        since=since,
        until=until,
    )
    return APIResponse(
        data=AuditLogListResponse(
            logs=[AuditLogResponse.model_validate(log) for log in logs],
            total=total,
        ),
        meta=MetaInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page,
        ),
    )
