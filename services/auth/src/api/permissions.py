"""権限一覧エンドポイント"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    MetaInfo,
    PermissionListResponse,
    PermissionResponse,
    TokenData,
)
from ..services.permission_service import get_permissions_paginated

router = APIRouter()


@router.get("", response_model=APIResponse[PermissionListResponse])
async def list_permissions(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    resource: str | None = Query(None),
    action: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("permissions", "read")),
):
    """権限一覧取得(ページネーション・resource/actionフィルタ)"""
    permissions, total = await get_permissions_paginated(
        db, page=page, per_page=per_page, resource=resource, action=action
    )
    return APIResponse(
        data=PermissionListResponse(
            permissions=[PermissionResponse.model_validate(p) for p in permissions],
            total=total,
        ),
        meta=MetaInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page,
        ),
    )
