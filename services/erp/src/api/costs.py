"""原価管理 API"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas.schemas import (
    CostApproveRequest,
    CostCreateRequest,
    CostItemResponse,
    CostListResponse,
    CostUpdateRequest,
)
from ..services import cost_service, ledger_service

router = APIRouter()


@router.post(
    "/ledger/{ledger_id}/costs",
    response_model=CostItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_cost(
    ledger_id: UUID,
    body: CostCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    ledger = await ledger_service.get_ledger(db, ledger_id)
    if not ledger:
        raise HTTPException(status_code=404, detail="工事台帳が見つかりません")
    return await cost_service.create_cost(db, ledger_id, body.model_dump())


@router.get(
    "/ledger/{ledger_id}/costs", response_model=CostListResponse
)
async def list_costs(
    ledger_id: UUID,
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    ledger = await ledger_service.get_ledger(db, ledger_id)
    if not ledger:
        raise HTTPException(status_code=404, detail="工事台帳が見つかりません")
    items, total = await cost_service.list_costs(
        db, ledger_id, status=status, page=page, per_page=per_page
    )
    return CostListResponse(items=items, total=total, page=page, per_page=per_page)  # type: ignore[arg-type]


@router.put("/costs/{cost_id}", response_model=CostItemResponse)
async def update_cost(
    cost_id: UUID,
    body: CostUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    cost = await cost_service.get_cost(db, cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="原価明細が見つかりません")
    try:
        return await cost_service.update_cost(
            db, cost, body.model_dump(exclude_none=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/costs/{cost_id}/approve", response_model=CostItemResponse)
async def approve_cost(
    cost_id: UUID,
    body: CostApproveRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    cost = await cost_service.get_cost(db, cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="原価明細が見つかりません")
    try:
        return await cost_service.approve_cost(db, cost, body.approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/costs/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cost(
    cost_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    cost = await cost_service.get_cost(db, cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="原価明細が見つかりません")
    deleted = await cost_service.delete_cost(db, cost)
    if not deleted:
        raise HTTPException(
            status_code=400, detail="承認済みの原価は削除できません"
        )
    return None
