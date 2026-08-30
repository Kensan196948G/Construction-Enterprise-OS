"""権限管理ビジネスロジック"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Permission, RolePermission, UserRole


async def get_permissions_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    resource: str | None = None,
) -> tuple[list[Permission], int]:
    conditions = []
    if resource:
        conditions.append(Permission.resource == resource)

    base_query = select(Permission)
    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count()).select_from(Permission)
    if conditions:
        count_query = count_query.where(*conditions)
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        base_query.order_by(Permission.resource, Permission.action)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    permissions = list((await db.execute(query)).scalars().all())
    return permissions, total


async def user_has_permission(
    db: AsyncSession, user_id: uuid.UUID, resource: str, action: str
) -> bool:
    """ユーザーが (resource, action) の権限を、有効期限内のロール経由で保持しているか判定する"""
    now = datetime.now(timezone.utc)
    query = (
        select(func.count())
        .select_from(RolePermission)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(
            UserRole.user_id == user_id,
            Permission.resource == resource,
            Permission.action == action,
            or_(UserRole.expires_at.is_(None), UserRole.expires_at > now),
        )
    )
    count = (await db.execute(query)).scalar() or 0
    return count > 0
