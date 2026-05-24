"""自律制御指令管理エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    ControlListResponse,
    ControlResponse,
    ControlSendRequest,
)
from ..services.autonomous_service import (
    get_control_by_id,
    get_controls_for_target,
    get_pending_controls,
    send_control_command,
)

router = APIRouter()


def _ctrl_to_response(ctrl) -> ControlResponse:
    return ControlResponse.model_validate(ctrl)


@router.post("", response_model=APIResponse[ControlResponse], status_code=status.HTTP_201_CREATED)
async def send_command_endpoint(
    request: Request,
    body: ControlSendRequest,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    ctrl = await send_control_command(db, body.model_dump())
    return APIResponse(data=_ctrl_to_response(ctrl))


@router.get("", response_model=APIResponse[ControlListResponse])
async def list_pending_commands(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    organization_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    controls, total = await get_pending_controls(
        db,
        organization_id=organization_id,
        page=page,
        per_page=per_page,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total > 0 else 0

    return APIResponse(
        data=ControlListResponse(
            controls=[_ctrl_to_response(c) for c in controls],
            total=total,
        ),
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/{control_id}", response_model=APIResponse[ControlResponse])
async def get_command(
    request: Request,
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    ctrl = await get_control_by_id(db, control_id)
    if not ctrl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONTROL_NOT_FOUND", "message": "制御指令が見つかりません。"},
        )
    return APIResponse(data=_ctrl_to_response(ctrl))


@router.get("/target/{target_type}/{target_id}", response_model=APIResponse[ControlListResponse])
async def get_target_command_history(
    request: Request,
    target_type: str,
    target_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    controls, total = await get_controls_for_target(
        db,
        target_id=target_id,
        target_type=target_type,
        page=page,
        per_page=per_page,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total > 0 else 0

    return APIResponse(
        data=ControlListResponse(
            controls=[_ctrl_to_response(c) for c in controls],
            total=total,
        ),
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )
