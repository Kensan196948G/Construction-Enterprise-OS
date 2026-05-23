"""ロール管理エンドポイント"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth_middleware import require_permission
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    PermissionSummary,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    TokenData,
)
from ..services.role_service import (
    assign_permission_to_role,
    create_role,
    delete_role,
    get_roles,
    get_role_by_id,
    remove_permission_from_role,
    update_role,
)

router = APIRouter()


def _role_to_response(role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        organization_id=role.organization_id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        permissions=[
            PermissionSummary(
                id=rp.permission.id,
                resource=rp.permission.resource,
                action=rp.permission.action,
            )
            for rp in role.permissions
        ],
    )


@router.get("", response_model=APIResponse[list[RoleResponse]])
async def list_roles(
    request: Request,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "read")),
):
    """ロール一覧取得"""
    roles = await get_roles(db, org_id)
    return APIResponse(data=[_role_to_response(r) for r in roles])


@router.post("", response_model=APIResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    request: Request,
    body: RoleCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "create")),
):
    """ロール作成"""
    role = await create_role(
        db,
        organization_id=body.organization_id,
        name=body.name,
        description=body.description,
        permission_ids=body.permission_ids,
    )
    await db.flush()
    created = await get_role_by_id(db, role.id)
    return APIResponse(data=_role_to_response(created))


@router.get("/{role_id}", response_model=APIResponse[RoleResponse])
async def get_role(
    request: Request,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "read")),
):
    """ロール詳細取得"""
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ROLE_NOT_FOUND", "message": "ロールが見つかりません。"},
        )
    return APIResponse(data=_role_to_response(role))


@router.put("/{role_id}", response_model=APIResponse[RoleResponse])
async def update_role_endpoint(
    request: Request,
    role_id: UUID,
    body: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "update")),
):
    """ロール更新"""
    role = await update_role(
        db,
        role_id,
        name=body.name,
        description=body.description,
    )
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ROLE_NOT_FOUND", "message": "ロールが見つかりません。"},
        )
    return APIResponse(data=_role_to_response(role))


@router.delete("/{role_id}", response_model=APIResponse)
async def delete_role_endpoint(
    request: Request,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "delete")),
):
    """ロール削除"""
    success = await delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ROLE_NOT_FOUND", "message": "ロールが見つからないか、システムロールは削除できません。"},
        )
    return APIResponse(data={"message": "ロールを削除しました。"})


@router.post("/{role_id}/permissions", response_model=APIResponse[RoleResponse])
async def assign_permission(
    request: Request,
    role_id: UUID,
    perm_id: UUID = Query(..., alias="permission_id"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "update")),
):
    """ロールに権限を付与"""
    success = await assign_permission_to_role(db, role_id, perm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ROLE_NOT_FOUND", "message": "ロールが見つからないか、システムロールは変更できません。"},
        )
    role = await get_role_by_id(db, role_id)
    return APIResponse(data=_role_to_response(role))


@router.delete("/{role_id}/permissions/{perm_id}", response_model=APIResponse[RoleResponse])
async def remove_permission(
    request: Request,
    role_id: UUID,
    perm_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_permission("roles", "update")),
):
    """ロールから権限を削除"""
    success = await remove_permission_from_role(db, role_id, perm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PERMISSION_NOT_FOUND", "message": "権限が見つからないか、システムロールは変更できません。"},
        )
    role = await get_role_by_id(db, role_id)
    return APIResponse(data=_role_to_response(role))
