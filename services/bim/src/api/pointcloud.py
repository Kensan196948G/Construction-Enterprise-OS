"""点群データ管理 API"""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models import PointCloud
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    MetaInfo,
    PointCloudCreate,
    PointCloudResponse,
    PointCloudUpdate,
)

router = APIRouter()


def _api_response(data=None, meta=None, error=None, success=True):
    return APIResponse(success=success, data=data, error=error, meta=meta)


def _pc_to_response(pc: PointCloud) -> dict:
    return PointCloudResponse.model_validate(pc).model_dump(mode="json")


@router.post("")
async def create_pointcloud(
    body: PointCloudCreate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pc = PointCloud(
        organization_id=body.organization_id,
        project_id=body.project_id,
        name=body.name,
        description=body.description,
        capture_method=body.capture_method,
        capture_date=body.capture_date,
        point_count=body.point_count,
        file_size=body.file_size,
        file_format=body.file_format,
        file_key=body.file_key,
        coordinate_system=body.coordinate_system,
        bounding_box=body.bounding_box,
        density=body.density,
        accuracy_mm=body.accuracy_mm,
        is_colorized=body.is_colorized,
        is_classified=body.is_classified,
        metadata_=body.metadata,
        uploaded_by=UUID(token_data.sub),
    )
    db.add(pc)
    await db.flush()
    await db.refresh(pc)
    return _api_response(data=_pc_to_response(pc))


@router.get("")
async def list_pointclouds(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    project_id: UUID | None = Query(None),
    capture_method: str | None = Query(None),
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PointCloud)
    count_query = select(func.count(PointCloud.id))

    if project_id:
        query = query.where(PointCloud.project_id == project_id)
        count_query = count_query.where(PointCloud.project_id == project_id)
    if capture_method:
        query = query.where(PointCloud.capture_method == capture_method)
        count_query = count_query.where(PointCloud.capture_method == capture_method)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    query = query.order_by(PointCloud.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    pointclouds = result.scalars().all()

    meta = MetaInfo(page=page, per_page=per_page, total=total, total_pages=total_pages)
    return _api_response(
        data=[_pc_to_response(pc) for pc in pointclouds], meta=meta
    )


@router.get("/{pointcloud_id}")
async def get_pointcloud(
    pointcloud_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PointCloud).where(PointCloud.id == pointcloud_id)
    )
    pc = result.scalar_one_or_none()
    if not pc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "点群データが見つかりません。"},
        )
    return _api_response(data=_pc_to_response(pc))


@router.put("/{pointcloud_id}")
async def update_pointcloud(
    pointcloud_id: UUID,
    body: PointCloudUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PointCloud).where(PointCloud.id == pointcloud_id)
    )
    pc = result.scalar_one_or_none()
    if not pc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "点群データが見つかりません。"},
        )

    update_data = body.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")

    for key, value in update_data.items():
        setattr(pc, key, value)

    await db.flush()
    await db.refresh(pc)
    return _api_response(data=_pc_to_response(pc))


@router.delete("/{pointcloud_id}")
async def delete_pointcloud(
    pointcloud_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PointCloud).where(PointCloud.id == pointcloud_id)
    )
    pc = result.scalar_one_or_none()
    if not pc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "点群データが見つかりません。"},
        )
    await db.delete(pc)
    await db.flush()
    return _api_response(data={"deleted": True})
