"""イベントトリガー管理エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    TriggerCreateRequest,
    TriggerListResponse,
    TriggerResponse,
    TriggerUpdateRequest,
)
from ..services.automation_service import (
    create_trigger,
    delete_trigger,
    disable_trigger,
    enable_trigger,
    get_trigger_by_id,
    get_triggers_paginated,
    update_trigger,
)

router = APIRouter()


def _trigger_to_response(trigger) -> TriggerResponse:
    return TriggerResponse.model_validate(trigger)


@router.post("", response_model=APIResponse[TriggerResponse], status_code=status.HTTP_201_CREATED)
async def create_trigger_endpoint(
    request: Request,
    body: TriggerCreateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    trigger = await create_trigger(db, body.model_dump())
    return APIResponse(data=_trigger_to_response(trigger))


@router.get("", response_model=APIResponse[TriggerListResponse])
async def list_triggers(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    event_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    organization_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    triggers_items, total = await get_triggers_paginated(
        db,
        page=page,
        per_page=per_page,
        event_type=event_type,
        is_active=is_active,
        organization_id=organization_id,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total > 0 else 0

    return APIResponse(
        data=TriggerListResponse(
            triggers=[_trigger_to_response(t) for t in triggers_items],
            total=total,
        ),
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/{trigger_id}", response_model=APIResponse[TriggerResponse])
async def get_trigger(
    request: Request,
    trigger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    trigger = await get_trigger_by_id(db, trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIGGER_NOT_FOUND", "message": "トリガーが見つかりません。"},
        )
    return APIResponse(data=_trigger_to_response(trigger))


@router.put("/{trigger_id}", response_model=APIResponse[TriggerResponse])
async def update_trigger_endpoint(
    request: Request,
    trigger_id: UUID,
    body: TriggerUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    trigger = await update_trigger(db, trigger_id, body.model_dump(exclude_unset=True))
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIGGER_NOT_FOUND", "message": "トリガーが見つかりません。"},
        )
    return APIResponse(data=_trigger_to_response(trigger))


@router.delete("/{trigger_id}", response_model=APIResponse)
async def delete_trigger_endpoint(
    request: Request,
    trigger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    deleted = await delete_trigger(db, trigger_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIGGER_NOT_FOUND", "message": "トリガーが見つかりません。"},
        )
    return APIResponse(data={"message": "トリガーを削除しました。"})


@router.post("/{trigger_id}/enable", response_model=APIResponse[TriggerResponse])
async def enable_trigger_endpoint(
    request: Request,
    trigger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    trigger = await enable_trigger(db, trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIGGER_NOT_FOUND", "message": "トリガーが見つかりません。"},
        )
    return APIResponse(data=_trigger_to_response(trigger))


@router.post("/{trigger_id}/disable", response_model=APIResponse[TriggerResponse])
async def disable_trigger_endpoint(
    request: Request,
    trigger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    trigger = await disable_trigger(db, trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIGGER_NOT_FOUND", "message": "トリガーが見つかりません。"},
        )
    return APIResponse(data=_trigger_to_response(trigger))
