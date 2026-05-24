"""品質管理 API"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import (
    QualityCheckCreateRequest,
    QualityCheckListResponse,
    QualityCheckResponse,
    QualityCheckUpdateRequest,
    QualityStatsResponse,
)
from ..services import field_service

router = APIRouter()


@router.post(
    "/quality",
    response_model=QualityCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_quality_check(
    body: QualityCheckCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    check = await field_service.create_quality_check(db, body.model_dump())
    return check


@router.get("/quality", response_model=QualityCheckListResponse)
async def list_quality_checks(
    organization_id: UUID | None = Query(None),
    project_id: UUID | None = Query(None),
    check_type: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    items, total = await field_service.list_quality_checks(
        db,
        organization_id=organization_id,
        project_id=project_id,
        check_type=check_type,
        status=status,
        page=page,
        per_page=per_page,
    )
    return QualityCheckListResponse(
        items=items, total=total, page=page, per_page=per_page
    )


@router.put("/quality/{check_id}", response_model=QualityCheckResponse)
async def update_quality_check(
    check_id: UUID,
    body: QualityCheckUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    check = await field_service.get_quality_check(db, check_id)
    if not check:
        raise HTTPException(status_code=404, detail="品質チェックが見つかりません")
    return await field_service.update_quality_check(
        db, check, body.model_dump(exclude_none=True)
    )


@router.get(
    "/quality/{project_id}/stats",
    response_model=QualityStatsResponse,
)
async def quality_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    return await field_service.get_quality_stats(db, project_id)
