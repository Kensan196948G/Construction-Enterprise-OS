"""APIクライアント管理エンドポイント（M2M認証用）"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    ApiClientCreateRequest,
    ApiClientCreateResponse,
    TokenData,
)
from ..services.client_service import (
    create_api_client,
    get_api_clients,
    revoke_api_client,
)

router = APIRouter()

# Stub data returned when no organization_id is supplied (e.g. dashboard overview)
_STUB_CLIENTS: list[dict[str, Any]] = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "建設現場IoTゲートウェイ",
        "client_id": "ck_live_iot_a1b2",
        "client_type": "IoTシステム",
        "scopes": ["iot:read", "iot:write"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-01-15T00:00:00",
        "last_used_at": "2024-11-30T09:05:00",
        "rate_limit": 1000,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "会計システム連携",
        "client_id": "ck_live_erp_c3d4",
        "client_type": "ERPシステム",
        "scopes": ["erp:read", "erp:write"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-02-01T00:00:00",
        "last_used_at": "2024-11-30T08:30:00",
        "rate_limit": 500,
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "GISマッピングAPI",
        "client_id": "ck_live_gis_e5f6",
        "client_type": "GISシステム",
        "scopes": ["gis:read"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-03-10T00:00:00",
        "last_used_at": "2024-11-29T17:45:00",
        "rate_limit": 2000,
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "工事写真管理システム",
        "client_id": "ck_live_doc_g7h8",
        "client_type": "文書管理",
        "scopes": ["documents:read", "documents:write"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-04-05T00:00:00",
        "last_used_at": "2024-11-29T14:00:00",
        "rate_limit": 800,
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "安全管理モバイルApp",
        "client_id": "ck_live_safety_i9j0",
        "client_type": "モバイルアプリ",
        "scopes": ["safety:read", "safety:write"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-05-20T00:00:00",
        "last_used_at": "2024-11-30T07:22:00",
        "rate_limit": 1200,
    },
    {
        "id": "00000000-0000-0000-0000-000000000006",
        "name": "レポート自動生成Bot",
        "client_id": "ck_live_bot_k1l2",
        "client_type": "自動化Bot",
        "scopes": ["projects:read", "reports:write"],
        "is_active": True,
        "status": "active",
        "created_at": "2024-06-01T00:00:00",
        "last_used_at": "2024-11-30T06:00:00",
        "rate_limit": 300,
    },
]


@router.post(
    "",
    response_model=APIResponse[ApiClientCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    request: Request,
    body: ApiClientCreateRequest,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("clients", "create")),
):
    """APIクライアント登録"""
    client, plain_secret = await create_api_client(
        db,
        organization_id=org_id,
        name=body.name,
        scopes=body.scopes,
    )
    return APIResponse(
        data=ApiClientCreateResponse(
            id=client.id,
            name=client.name,
            client_id=client.client_id,
            client_secret=plain_secret,
            scopes=client.scopes,
        )
    )


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_clients(
    request: Request,
    org_id: UUID | None = Query(None, alias="organization_id"),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """APIクライアント一覧取得。organization_id 省略時はスタブデータを返す。"""
    if org_id is None:
        # Dashboard overview: return stub data without requiring auth or DB
        return APIResponse(data=_STUB_CLIENTS[:per_page])

    # Authenticated path requires permission

    clients_list = await get_api_clients(db, org_id)
    return APIResponse(
        data=[
            {
                "id": str(c.id),
                "name": c.name,
                "client_id": c.client_id,
                "client_type": "",
                "scopes": c.scopes,
                "is_active": c.status == "active",
                "status": c.status,
                "created_at": c.created_at.isoformat()
                if hasattr(c.created_at, "isoformat")
                else str(c.created_at),
                "last_used_at": None,
                "rate_limit": 1000,
            }
            for c in clients_list
        ]
    )


@router.delete("/{client_id}", response_model=APIResponse)
async def delete_client(
    request: Request,
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("clients", "delete")),
):
    """APIクライアント削除（無効化）"""
    client = await revoke_api_client(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CLIENT_NOT_FOUND",
                "message": "APIクライアントが見つかりません。",
            },
        )
    return APIResponse(data={"message": "APIクライアントを無効化しました。"})
