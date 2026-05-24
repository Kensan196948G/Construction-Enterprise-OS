"""出来形・進捗管理 API"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import (
    ProgressCreateRequest,
    ProgressListResponse,
    ProgressResponse,
    ProgressSummaryResponse,
    ProgressUpdateRequest,
)
from ..services import field_service

router = APIRouter()


@router.post(
    "/progress",
    response_model=ProgressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_progress(
    body: ProgressCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    record = await field_service.create_progress_record(db, body.model_dump())
    return record


@router.get("/progress", response_model=ProgressListResponse)
async def list_progress(
    organization_id: UUID | None = Query(None),
    project_id: UUID | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    items, total = await field_service.list_progress_records(
        db,
        organization_id=organization_id,
        project_id=project_id,
        status=status,
        page=page,
        per_page=per_page,
    )
    return ProgressListResponse(
        items=items, total=total, page=page, per_page=per_page
    )


@router.put("/progress/{record_id}", response_model=ProgressResponse)
async def update_progress(
    record_id: UUID,
    body: ProgressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    record = await field_service.get_progress_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="進捗記録が見つかりません")
    return await field_service.update_progress_record(
        db, record, body.model_dump(exclude_none=True)
    )


@router.get(
    "/progress/{project_id}/summary",
    response_model=ProgressSummaryResponse,
)
async def progress_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    return await field_service.get_progress_summary(db, project_id)
