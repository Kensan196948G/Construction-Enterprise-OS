"""BIMモデル管理 API"""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models import BIMModel
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    BIMModelCreate,
    BIMModelResponse,
    BIMModelUpdate,
    MetaInfo,
)

router = APIRouter()


def _api_response(data=None, meta=None, error=None, success=True):
    return APIResponse(success=success, data=data, error=error, meta=meta)


def _model_to_response(m: BIMModel) -> dict:
    return BIMModelResponse.model_validate(m).model_dump(mode="json")


@router.post("")
async def create_model(
    body: BIMModelCreate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    model = BIMModel(
        organization_id=body.organization_id,
        project_id=body.project_id,
        name=body.name,
        description=body.description,
        model_type=body.model_type,
        file_format=body.file_format,
        file_size=body.file_size,
        file_key=body.file_key,
        version=body.version,
        status=body.status,
        author=body.author,
        software=body.software,
        coordinate_system=body.coordinate_system,
        bounding_box=body.bounding_box,
        discipline=body.discipline,
        lod=body.lod,
        tags=body.tags,
        metadata_=body.metadata,
        uploaded_by=UUID(token_data.sub),
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return _api_response(data=_model_to_response(model))


@router.get("")
async def list_models(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    model_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    project_id: UUID | None = Query(None),
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(BIMModel)
    count_query = select(func.count(BIMModel.id))

    if model_type:
        query = query.where(BIMModel.model_type == model_type)
        count_query = count_query.where(BIMModel.model_type == model_type)
    if status_filter:
        query = query.where(BIMModel.status == status_filter)
        count_query = count_query.where(BIMModel.status == status_filter)
    if project_id:
        query = query.where(BIMModel.project_id == project_id)
        count_query = count_query.where(BIMModel.project_id == project_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    query = query.order_by(BIMModel.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    models = result.scalars().all()

    meta = MetaInfo(page=page, per_page=per_page, total=total, total_pages=total_pages)
    return _api_response(
        data=[_model_to_response(m) for m in models], meta=meta
    )


@router.get("/{model_id}")
async def get_model(
    model_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BIMModel).where(BIMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "BIMモデルが見つかりません。"},
        )
    return _api_response(data=_model_to_response(model))


@router.put("/{model_id}")
async def update_model(
    model_id: UUID,
    body: BIMModelUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BIMModel).where(BIMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "BIMモデルが見つかりません。"},
        )

    update_data = body.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    if "status_filter" in update_data:
        update_data.pop("status_filter", None)

    for key, value in update_data.items():
        setattr(model, key, value)

    await db.flush()
    await db.refresh(model)
    return _api_response(data=_model_to_response(model))


@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BIMModel).where(BIMModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "BIMモデルが見つかりません。"},
        )
    await db.delete(model)
    await db.flush()
    return _api_response(data={"deleted": True})
