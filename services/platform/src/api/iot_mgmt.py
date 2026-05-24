"""IoTデバイス管理・ダッシュボード API"""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models import IoTDashboard, DeviceGroup
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    MetaInfo,
    IoTDashboardCreate,
    IoTDashboardResponse,
    IoTDashboardUpdate,
    DeviceGroupCreate,
    DeviceGroupResponse,
    DeviceGroupUpdate,
)

router = APIRouter()


def _api_response(data=None, meta=None, error=None, success=True):
    return APIResponse(success=success, data=data, error=error, meta=meta)


def _dashboard_to_response(d: IoTDashboard) -> dict:
    return IoTDashboardResponse.model_validate(d).model_dump(mode="json")


def _group_to_response(g: DeviceGroup) -> dict:
    return DeviceGroupResponse.model_validate(g).model_dump(mode="json")


# === IoT Dashboards ===

@router.post("/dashboards")
async def create_dashboard(
    body: IoTDashboardCreate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dashboard = IoTDashboard(
        organization_id=body.organization_id,
        project_id=body.project_id,
        name=body.name,
        description=body.description,
        layout=body.layout,
        refresh_interval_seconds=body.refresh_interval_seconds,
        is_public=body.is_public,
        created_by=UUID(token_data.sub),
    )
    db.add(dashboard)
    await db.flush()
    await db.refresh(dashboard)
    return _api_response(data=_dashboard_to_response(dashboard))


@router.get("/dashboards")
async def list_dashboards(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    project_id: UUID | None = Query(None),
    is_public: bool | None = Query(None),
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IoTDashboard)
    count_query = select(func.count(IoTDashboard.id))

    if project_id:
        query = query.where(IoTDashboard.project_id == project_id)
        count_query = count_query.where(IoTDashboard.project_id == project_id)
    if is_public is not None:
        query = query.where(IoTDashboard.is_public == is_public)
        count_query = count_query.where(IoTDashboard.is_public == is_public)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    query = query.order_by(IoTDashboard.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    dashboards = result.scalars().all()

    meta = MetaInfo(page=page, per_page=per_page, total=total, total_pages=total_pages)
    return _api_response(
        data=[_dashboard_to_response(d) for d in dashboards], meta=meta
    )


@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(
    dashboard_id: UUID,
    body: IoTDashboardUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IoTDashboard).where(IoTDashboard.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "ダッシュボードが見つかりません。"},
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dashboard, key, value)

    await db.flush()
    await db.refresh(dashboard)
    return _api_response(data=_dashboard_to_response(dashboard))


# === Device Groups ===

@router.post("/device-groups")
async def create_device_group(
    body: DeviceGroupCreate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = DeviceGroup(
        organization_id=body.organization_id,
        name=body.name,
        description=body.description,
        device_ids=body.device_ids,
        group_type=body.group_type,
        parent_group_id=body.parent_group_id,
    )
    db.add(group)
    await db.flush()
    await db.refresh(group)
    return _api_response(data=_group_to_response(group))


@router.get("/device-groups")
async def list_device_groups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    group_type: str | None = Query(None),
    parent_group_id: UUID | None = Query(None),
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(DeviceGroup)
    count_query = select(func.count(DeviceGroup.id))

    if group_type:
        query = query.where(DeviceGroup.group_type == group_type)
        count_query = count_query.where(DeviceGroup.group_type == group_type)
    if parent_group_id is not None:
        query = query.where(DeviceGroup.parent_group_id == parent_group_id)
        count_query = count_query.where(DeviceGroup.parent_group_id == parent_group_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    query = query.order_by(DeviceGroup.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    groups = result.scalars().all()

    meta = MetaInfo(page=page, per_page=per_page, total=total, total_pages=total_pages)
    return _api_response(
        data=[_group_to_response(g) for g in groups], meta=meta
    )


@router.put("/device-groups/{group_id}/devices")
async def update_device_group_devices(
    group_id: UUID,
    body: DeviceGroupUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DeviceGroup).where(DeviceGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "デバイスグループが見つかりません。"},
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await db.flush()
    await db.refresh(group)
    return _api_response(data=_group_to_response(group))


@router.get("/device-groups/{group_id}")
async def get_device_group(
    group_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DeviceGroup).where(DeviceGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "デバイスグループが見つかりません。"},
        )
    return _api_response(data=_group_to_response(group))
