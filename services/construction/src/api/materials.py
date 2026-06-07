"""建設資材マスタ API — 施工で使用する資材・部材の一覧を提供する。"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class MaterialResponse(BaseModel):
    id: str
    code: str
    name: str
    category: str
    unit: str
    unit_price: float
    supplier: str
    is_active: bool


class MaterialListResponse(BaseModel):
    items: list[MaterialResponse]
    total: int


MOCK_MATERIALS: list[MaterialResponse] = [
    MaterialResponse(
        id="mat-001",
        code="STL-H200",
        name="H形鋼 200×200",
        category="鉄骨材料",
        unit="kg",
        unit_price=185.0,
        supplier="日本製鉄株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-002",
        code="CON-C30",
        name="コンクリートC30",
        category="コンクリート",
        unit="m³",
        unit_price=18500.0,
        supplier="太平洋セメント株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-003",
        code="REB-D25",
        name="鉄筋D25",
        category="鉄筋材料",
        unit="kg",
        unit_price=95.0,
        supplier="東京製鐵株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-004",
        code="PST-BAR",
        name="PC鋼棒",
        category="PC材料",
        unit="kg",
        unit_price=320.0,
        supplier="神鋼鋼線工業株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-005",
        code="PIP-FRPM600",
        name="FRPM管 φ600",
        category="管材",
        unit="m",
        unit_price=48000.0,
        supplier="積水化学工業株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-006",
        code="SHT-WP",
        name="防水シート",
        category="防水材料",
        unit="m²",
        unit_price=850.0,
        supplier="田島ルーフィング株式会社",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-007",
        code="PLY-FORM",
        name="型枠合板",
        category="仮設材料",
        unit="枚",
        unit_price=1200.0,
        supplier="株式会社ノダ",
        is_active=True,
    ),
    MaterialResponse(
        id="mat-008",
        code="AGG-40",
        name="砕石 40mm",
        category="骨材",
        unit="m³",
        unit_price=3800.0,
        supplier="地元砕石株式会社",
        is_active=False,
    ),
]


@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str | None = Query(None, description="資材カテゴリでフィルタ"),
    is_active: bool | None = Query(None, description="有効/無効フィルタ"),
) -> MaterialListResponse:
    """建設資材マスタ一覧を返す。"""
    items: list[MaterialResponse] = MOCK_MATERIALS

    if category is not None:
        items = [m for m in items if m.category == category]
    if is_active is not None:
        items = [m for m in items if m.is_active == is_active]

    total = len(items)
    start = (page - 1) * per_page
    return MaterialListResponse(items=items[start : start + per_page], total=total)
