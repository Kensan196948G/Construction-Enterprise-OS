"""Entra ID (Azure AD) 統合エンドポイント"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class ConditionalPolicyResponse(BaseModel):
    id: str
    name: str
    target: str
    condition: str
    action: str
    status: str


class ConditionalPolicyListResponse(BaseModel):
    items: list[ConditionalPolicyResponse]
    total: int


MOCK_POLICIES = [
    ConditionalPolicyResponse(
        id="p1",
        name="管理者MFA強制",
        target="役割: システム管理者",
        condition="全てのアクセス",
        action="MFA要求",
        status="enabled",
    ),
    ConditionalPolicyResponse(
        id="p2",
        name="社外アクセス制限",
        target="全ユーザー",
        condition="社外ネットワーク",
        action="準拠デバイス要求",
        status="enabled",
    ),
    ConditionalPolicyResponse(
        id="p3",
        name="レガシー認証ブロック",
        target="全ユーザー",
        condition="レガシープロトコル",
        action="ブロック",
        status="enabled",
    ),
    ConditionalPolicyResponse(
        id="p4",
        name="高リスクサインインブロック",
        target="全ユーザー",
        condition="高リスクサインイン",
        action="アクセスブロック",
        status="enabled",
    ),
    ConditionalPolicyResponse(
        id="p5",
        name="サービスアカウント例外",
        target="サービスアカウント",
        condition="信頼済みIPアドレス",
        action="許可（MFA除外）",
        status="disabled",
    ),
]


@router.get("/policies", response_model=ConditionalPolicyListResponse)
async def list_entra_policies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    start = (page - 1) * per_page
    return ConditionalPolicyListResponse(
        items=MOCK_POLICIES[start : start + per_page], total=len(MOCK_POLICIES)
    )
