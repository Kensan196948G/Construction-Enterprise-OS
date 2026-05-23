"""ユーザー管理エンドポイント"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import get_current_user, require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    TokenData,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter()


@router.get("", response_model=APIResponse[UserListResponse])
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "read")),
):
    """ユーザー一覧取得（ページネーション・検索・フィルタ）"""
    # TODO: 本実装
    return APIResponse(
        data=UserListResponse(users=[], total=0),
        meta={"page": page, "per_page": per_page, "total": 0, "total_pages": 0},
    )


@router.post("", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    body: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "create")),
):
    """ユーザー作成"""
    # TODO: 本実装
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    request: Request,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """ユーザー詳細取得"""
    # TODO: 本実装
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    request: Request,
    user_id: str,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "update")),
):
    """ユーザー情報更新"""
    # TODO: 本実装
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    request: Request,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "delete")),
):
    """ユーザー削除（論理削除）"""
    # TODO: 本実装
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
