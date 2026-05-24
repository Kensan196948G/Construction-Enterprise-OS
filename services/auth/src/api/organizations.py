"""組織管理 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class Organization(BaseModel):
    id: str
    code: str
    name: str
    name_kana: str
    org_type: str
    status: str
    address: str
    phone: str
    member_count: int


_MOCK_ORGS = [
    Organization(
        id="org1",
        code="HQ-001",
        name="建設本社",
        name_kana="ケンセツホンシャ",
        org_type="本社",
        status="active",
        address="東京都千代田区丸の内1-1-1",
        phone="03-1234-5678",
        member_count=120,
    ),
    Organization(
        id="org2",
        code="BR-001",
        name="東京支店",
        name_kana="トウキョウシテン",
        org_type="支店",
        status="active",
        address="東京都新宿区西新宿2-2-2",
        phone="03-2345-6789",
        member_count=45,
    ),
    Organization(
        id="org3",
        code="BR-002",
        name="大阪支店",
        name_kana="オオサカシテン",
        org_type="支店",
        status="active",
        address="大阪府大阪市北区梅田3-3-3",
        phone="06-3456-7890",
        member_count=38,
    ),
    Organization(
        id="org4",
        code="SITE-001",
        name="第一工事現場",
        name_kana="ダイイチコウジゲンバ",
        org_type="現場",
        status="active",
        address="東京都江東区有明4-4-4",
        phone="03-4567-8901",
        member_count=15,
    ),
]


@router.get("/organizations")
async def list_organizations(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_ORGS[start : start + per_page]
    return {
        "data": {"items": [o.model_dump() for o in items], "total": len(_MOCK_ORGS)}
    }
