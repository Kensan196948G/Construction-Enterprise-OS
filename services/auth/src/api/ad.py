"""Active Directory統合エンドポイント"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class ADGroupMappingResponse(BaseModel):
    id: str
    ad_group: str
    system_role: str
    members: int


class ADGroupMappingListResponse(BaseModel):
    items: list[ADGroupMappingResponse]
    total: int


MOCK_AD_GROUPS = [
    ADGroupMappingResponse(
        id="g1",
        ad_group="CN=システム管理者,OU=建設部門,DC=company,DC=local",
        system_role="system_admin",
        members=3,
    ),
    ADGroupMappingResponse(
        id="g2",
        ad_group="CN=現場監督,OU=建設部門,DC=company,DC=local",
        system_role="site_supervisor",
        members=24,
    ),
    ADGroupMappingResponse(
        id="g3",
        ad_group="CN=設計部門,OU=技術部門,DC=company,DC=local",
        system_role="design_engineer",
        members=18,
    ),
    ADGroupMappingResponse(
        id="g4",
        ad_group="CN=経理部門,OU=管理部門,DC=company,DC=local",
        system_role="finance_manager",
        members=8,
    ),
    ADGroupMappingResponse(
        id="g5",
        ad_group="CN=閲覧専用,OU=全社員,DC=company,DC=local",
        system_role="viewer",
        members=156,
    ),
]


@router.get("/groups", response_model=ADGroupMappingListResponse)
async def list_ad_groups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    start = (page - 1) * per_page
    return ADGroupMappingListResponse(
        items=MOCK_AD_GROUPS[start : start + per_page], total=len(MOCK_AD_GROUPS)
    )
