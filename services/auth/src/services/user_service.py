"""ユーザー管理ビジネスロジック"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import User, UserRole


async def get_users_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    search: str | None = None,
) -> tuple[list[User], int]:
    conditions = []
    if status:
        conditions.append(User.status == status)
    if search:
        conditions.append(
            or_(
                User.email.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )

    base_query = select(User)
    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count()).select_from(User)
    if conditions:
        count_query = count_query.where(*conditions)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    query = (
        base_query
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total


async def create_user(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    email: str,
    username: str | None,
    hashed_password: str,
    display_name: str,
    phone: str | None,
    role_ids: list[uuid.UUID] | None = None,
) -> User:
    user = User(
        id=uuid.uuid4(),
        organization_id=organization_id,
        email=email,
        username=username,
        hashed_password=hashed_password,
        display_name=display_name,
        phone=phone,
        locale="ja",
        status="active",
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(user)

    if role_ids:
        for role_id in role_ids:
            user_role = UserRole(
                user_id=user.id,
                role_id=role_id,
                assigned_at=datetime.now(timezone.utc),
            )
            db.add(user_role)

    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    update_data: dict,
) -> User | None:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    allowed_fields = {"email", "display_name", "phone", "locale", "status"}
    for field, value in update_data.items():
        if field in allowed_fields and value is not None:
            setattr(user, field, value)

    return user


async def soft_delete_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    user.status = "deactivated"
    return user
