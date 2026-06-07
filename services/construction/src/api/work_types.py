"""工種マスタ API — 建設工事で使用する工種・作業種別の一覧を提供する。"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class WorkTypeResponse(BaseModel):
    id: str
    code: str
    name: str
    category: str
    unit: str
    standard_days: int
    is_active: bool


class WorkTypeListResponse(BaseModel):
    items: list[WorkTypeResponse]
    total: int


MOCK_WORK_TYPES: list[WorkTypeResponse] = [
    WorkTypeResponse(
        id="wt-001",
        code="FOUND",
        name="基礎工事",
        category="躯体工事",
        unit="式",
        standard_days=30,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-002",
        code="STRUC",
        name="躯体工事",
        category="躯体工事",
        unit="式",
        standard_days=60,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-003",
        code="EXT",
        name="外装工事",
        category="仕上工事",
        unit="m²",
        standard_days=20,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-004",
        code="ELEC",
        name="電気設備工事",
        category="設備工事",
        unit="式",
        standard_days=25,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-005",
        code="PLMB",
        name="給排水工事",
        category="設備工事",
        unit="式",
        standard_days=20,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-006",
        code="TEMP",
        name="仮設工事",
        category="仮設工事",
        unit="式",
        standard_days=5,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-007",
        code="EARTH",
        name="土工事",
        category="土工事",
        unit="m³",
        standard_days=15,
        is_active=True,
    ),
    WorkTypeResponse(
        id="wt-008",
        code="DEMO",
        name="解体工事",
        category="解体工事",
        unit="式",
        standard_days=10,
        is_active=False,
    ),
]


@router.get("", response_model=WorkTypeListResponse)
async def list_work_types(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str | None = Query(None, description="工種カテゴリでフィルタ"),
    is_active: bool | None = Query(None, description="有効/無効フィルタ"),
) -> WorkTypeListResponse:
    """工種マスタ一覧を返す。"""
    items: list[WorkTypeResponse] = MOCK_WORK_TYPES

    if category is not None:
        items = [w for w in items if w.category == category]
    if is_active is not None:
        items = [w for w in items if w.is_active == is_active]

    total = len(items)
    start = (page - 1) * per_page
    return WorkTypeListResponse(items=items[start : start + per_page], total=total)
