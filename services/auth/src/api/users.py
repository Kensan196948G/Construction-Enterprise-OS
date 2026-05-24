"""ユーザー管理エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import get_current_user, require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    MetaInfo,
    RoleSummary,
    TokenData,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from ..services.auth_service import hash_password, get_user_by_email
from ..services.user_service import (
    create_user as create_user_svc,
    get_user_by_id,
    get_users_paginated,
    soft_delete_user,
    update_user as update_user_svc,
)

router = APIRouter()


def _user_to_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        username=user.username,
        display_name=user.display_name,
        phone=user.phone,
        locale=user.locale,
        status=user.status,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        roles=[RoleSummary(id=ur.role.id, name=ur.role.name) for ur in user.roles],
    )


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
    users, total = await get_users_paginated(
        db, page=page, per_page=per_page, status=status, search=search
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total > 0 else 0

    return APIResponse(
        data=UserListResponse(
            users=[_user_to_response(u) for u in users],
            total=total,
        ),
        meta=MetaInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.post(
    "", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: Request,
    body: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "create")),
):
    """ユーザー作成"""
    existing = await get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_TAKEN",
                "message": "このメールアドレスは既に使用されています。",
            },
        )

    hashed = hash_password(body.password)
    user = await create_user_svc(
        db,
        organization_id=body.organization_id,
        email=body.email,
        username=body.username,
        hashed_password=hashed,
        display_name=body.display_name,
        phone=body.phone,
        role_ids=body.role_ids,
    )
    await db.flush()
    user_with_roles = await get_user_by_id(db, user.id)
    return APIResponse(data=_user_to_response(user_with_roles))


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    request: Request,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """ユーザー詳細取得"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません。"},
        )
    return APIResponse(data=_user_to_response(user))


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    request: Request,
    user_id: UUID,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "update")),
):
    """ユーザー情報更新"""
    update_dict = body.model_dump(exclude_unset=True)
    user = await update_user_svc(db, user_id, update_dict)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません。"},
        )
    return APIResponse(data=_user_to_response(user))


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    request: Request,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("users", "delete")),
):
    """ユーザー削除（論理削除）"""
    user = await soft_delete_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません。"},
        )
    return APIResponse(data={"message": "ユーザーを無効化しました。"})
