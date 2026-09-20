"""ETLパイプライン API"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import (
    PipelineCreateRequest,
    PipelineListResponse,
    PipelineResponse,
    PipelineRunResponse,
    PipelineUpdateRequest,
)
from ..services import analytics_service as service

router = APIRouter()


@router.post(
    "/pipelines",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_pipeline(
    body: PipelineCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    pipeline = await service.create_pipeline(db, body.model_dump())
    return pipeline


@router.get("/pipelines", response_model=PipelineListResponse)
async def list_pipelines(
    organization_id: UUID | None = Query(None),
    status: str | None = Query(None),
    source_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    items, total = await service.list_pipelines(
        db,
        organization_id=organization_id,
        status=status,
        source_id=source_id,
        page=page,
        per_page=per_page,
    )
    return PipelineListResponse(
        items=items, total=total, page=page, per_page=per_page  # type: ignore[arg-type]
    )


@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    pipeline = await service.get_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="パイプラインが見つかりません")
    return pipeline


@router.put("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: UUID,
    body: PipelineUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    pipeline = await service.get_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="パイプラインが見つかりません")
    return await service.update_pipeline(
        db, pipeline, body.model_dump(exclude_none=True)
    )


@router.delete("/pipelines/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    pipeline = await service.get_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="パイプラインが見つかりません")
    await service.delete_pipeline(db, pipeline)


@router.post(
    "/pipelines/{pipeline_id}/run",
    response_model=PipelineRunResponse,
)
async def trigger_pipeline_run(
    pipeline_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    pipeline = await service.get_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="パイプラインが見つかりません")
    if pipeline.status == "running":
        raise HTTPException(status_code=400, detail="パイプラインはすでに実行中です")
    result = await service.trigger_pipeline_run(db, pipeline)
    return result
