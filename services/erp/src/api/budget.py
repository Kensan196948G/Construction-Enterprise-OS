"""予算管理 API"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas.schemas import (
    BudgetCreateRequest,
    BudgetItemResponse,
    BudgetSummaryResponse,
    BudgetUpdateRequest,
)
from ..services import budget_service, ledger_service

router = APIRouter()


@router.post(
    "/ledger/{ledger_id}/budgets",
    response_model=BudgetItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget(
    ledger_id: UUID,
    body: BudgetCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    ledger = await ledger_service.get_ledger(db, ledger_id)
    if not ledger:
        raise HTTPException(status_code=404, detail="工事台帳が見つかりません")
    return await budget_service.create_budget(db, ledger_id, body.model_dump())


@router.get(
    "/ledger/{ledger_id}/budgets", response_model=list[BudgetItemResponse]
)
async def list_budgets(
    ledger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    ledger = await ledger_service.get_ledger(db, ledger_id)
    if not ledger:
        raise HTTPException(status_code=404, detail="工事台帳が見つかりません")
    return await budget_service.list_budgets(db, ledger_id)


@router.put("/budgets/{budget_id}", response_model=BudgetItemResponse)
async def update_budget(
    budget_id: UUID,
    body: BudgetUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    budget = await budget_service.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="予算項目が見つかりません")
    return await budget_service.update_budget(
        db, budget, body.model_dump(exclude_none=True)
    )


@router.get(
    "/ledger/{ledger_id}/budget-summary",
    response_model=BudgetSummaryResponse,
)
async def get_budget_summary(
    ledger_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenData = Depends(get_current_user),
):
    ledger = await ledger_service.get_ledger(db, ledger_id)
    if not ledger:
        raise HTTPException(status_code=404, detail="工事台帳が見つかりません")
    return await budget_service.get_budget_summary(db, ledger_id)
