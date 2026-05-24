"""ERP 資材マスタ API — 購買・原価管理に特化した資材マスタ一覧を提供する。"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class ErpMaterialResponse(BaseModel):
    id: str
    code: str
    name: str
    category: str
    unit: str
    last_purchase_price: float
    average_price: float
    stock_quantity: float
    reorder_point: float
    supplier_code: str


class ErpMaterialListResponse(BaseModel):
    items: list[ErpMaterialResponse]
    total: int


MOCK_ERP_MATERIALS: list[ErpMaterialResponse] = [
    ErpMaterialResponse(
        id="erp-mat-001",
        code="ERP-STL-001",
        name="鉄骨材料（H形鋼）",
        category="鉄骨材料",
        unit="kg",
        last_purchase_price=190.0,
        average_price=185.5,
        stock_quantity=12500.0,
        reorder_point=5000.0,
        supplier_code="SUP-NSC-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-002",
        code="ERP-CON-001",
        name="コンクリート（生コン）",
        category="コンクリート",
        unit="m³",
        last_purchase_price=19000.0,
        average_price=18600.0,
        stock_quantity=0.0,
        reorder_point=0.0,
        supplier_code="SUP-TPC-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-003",
        code="ERP-AGG-001",
        name="砂利・砂（細骨材）",
        category="骨材",
        unit="m³",
        last_purchase_price=3500.0,
        average_price=3650.0,
        stock_quantity=850.0,
        reorder_point=200.0,
        supplier_code="SUP-AGG-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-004",
        code="ERP-FRM-001",
        name="型枠（合板・支保工）",
        category="仮設材料",
        unit="m²",
        last_purchase_price=1100.0,
        average_price=1150.0,
        stock_quantity=3200.0,
        reorder_point=500.0,
        supplier_code="SUP-NOD-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-005",
        code="ERP-REB-001",
        name="鉄筋（異形棒鋼）",
        category="鉄筋材料",
        unit="kg",
        last_purchase_price=98.0,
        average_price=95.5,
        stock_quantity=28000.0,
        reorder_point=10000.0,
        supplier_code="SUP-TKS-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-006",
        code="ERP-WP-001",
        name="防水材（改質アスファルト）",
        category="防水材料",
        unit="m²",
        last_purchase_price=920.0,
        average_price=880.0,
        stock_quantity=1500.0,
        reorder_point=300.0,
        supplier_code="SUP-TJM-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-007",
        code="ERP-INS-001",
        name="断熱材（グラスウール）",
        category="断熱材料",
        unit="m²",
        last_purchase_price=680.0,
        average_price=665.0,
        stock_quantity=2200.0,
        reorder_point=400.0,
        supplier_code="SUP-MGA-001",
    ),
    ErpMaterialResponse(
        id="erp-mat-008",
        code="ERP-PIP-001",
        name="鋼管（配管用）",
        category="管材",
        unit="m",
        last_purchase_price=1850.0,
        average_price=1780.0,
        stock_quantity=620.0,
        reorder_point=100.0,
        supplier_code="SUP-NKK-001",
    ),
]


@router.get("", response_model=ErpMaterialListResponse)
async def list_erp_materials(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str | None = Query(None, description="資材カテゴリでフィルタ"),
    supplier_code: str | None = Query(None, description="仕入先コードでフィルタ"),
    low_stock: bool | None = Query(None, description="在庫発注点以下の資材のみ表示"),
) -> ErpMaterialListResponse:
    """ERP 資材マスタ一覧を返す（購買・原価管理用）。"""
    items: list[ErpMaterialResponse] = MOCK_ERP_MATERIALS

    if category is not None:
        items = [m for m in items if m.category == category]
    if supplier_code is not None:
        items = [m for m in items if m.supplier_code == supplier_code]
    if low_stock is True:
        items = [m for m in items if m.stock_quantity <= m.reorder_point]

    total = len(items)
    start = (page - 1) * per_page
    return ErpMaterialListResponse(items=items[start : start + per_page], total=total)
