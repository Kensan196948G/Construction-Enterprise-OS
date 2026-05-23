"""ロール・権限管理ビジネスロジック"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Role, RolePermission


async def create_role(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    name: str,
    description: str | None = None,
    permission_ids: list[uuid.UUID] | None = None,
) -> Role:
    role = Role(
        id=uuid.uuid4(),
        organization_id=organization_id,
        name=name,
        description=description,
        is_system=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(role)

    if permission_ids:
        for perm_id in permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=perm_id)
            db.add(rp)

    return role


async def get_roles(
    db: AsyncSession, organization_id: uuid.UUID
) -> list[Role]:
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
        .where(Role.organization_id == organization_id)
        .order_by(Role.created_at)
    )
    return list(result.scalars().all())


async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Role | None:
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
        .where(Role.id == role_id)
    )
    return result.scalar_one_or_none()


async def update_role(
    db: AsyncSession,
    role_id: uuid.UUID,
    name: str | None = None,
    description: str | None = None,
) -> Role | None:
    role = await get_role_by_id(db, role_id)
    if not role:
        return None
    if role.is_system:
        return None
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    return role


async def delete_role(db: AsyncSession, role_id: uuid.UUID) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role or role.is_system:
        return False
    await db.delete(role)
    return True


async def assign_permission_to_role(
    db: AsyncSession, role_id: uuid.UUID, permission_id: uuid.UUID
) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role or role.is_system:
        return False

    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )
    if result.scalar_one_or_none():
        return True  # already assigned, idempotent

    rp = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(rp)
    return True


async def remove_permission_from_role(
    db: AsyncSession, role_id: uuid.UUID, permission_id: uuid.UUID
) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role or role.is_system:
        return False

    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )
    rp = result.scalar_one_or_none()
    if rp:
        await db.delete(rp)
        return True
    return False
