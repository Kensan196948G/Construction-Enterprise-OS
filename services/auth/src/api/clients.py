"""APIクライアント管理エンドポイント（M2M認証用）"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    ApiClientCreateRequest,
    ApiClientCreateResponse,
    ApiClientResponse,
    TokenData,
)
from ..services.client_service import (
    create_api_client,
    get_api_clients,
    revoke_api_client,
)

router = APIRouter()


@router.post("", response_model=APIResponse[ApiClientCreateResponse], status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=APIResponse[list[ApiClientResponse]])
async def list_clients(
    request: Request,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("clients", "read")),
):
    """APIクライアント一覧取得"""
    clients = await get_api_clients(db, org_id)
    return APIResponse(
        data=[
            ApiClientResponse(
                id=c.id,
                name=c.name,
                client_id=c.client_id,
                scopes=c.scopes,
                status=c.status,
                created_at=c.created_at,
            )
            for c in clients
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
            detail={"code": "CLIENT_NOT_FOUND", "message": "APIクライアントが見つかりません。"},
        )
    return APIResponse(data={"message": "APIクライアントを無効化しました。"})
