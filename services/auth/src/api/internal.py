"""サービス間連携用の内部API。"""

import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import User, UserRole, Role
from ..models.base import get_db

router = APIRouter()


async def require_internal_api_key(
    x_internal_api_key: str | None = Header(default=None),
) -> None:
    configured = get_settings().INTERNAL_API_KEY
    if not configured or not x_internal_api_key or not secrets.compare_digest(
        x_internal_api_key, configured
    ):
        raise HTTPException(status_code=403, detail="内部認証が必要です。")


@router.get("/recipients", dependencies=[Depends(require_internal_api_key)])
async def list_notification_recipients(
    organization_id: UUID = Query(...),
    roles: str = Query(..., description="カンマ区切りのロール名"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    role_names = {name.strip() for name in roles.split(",") if name.strip()}
    if not role_names:
        return {"data": []}
    now = datetime.now(timezone.utc)
    query = (
        select(User.id)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .where(
            User.organization_id == organization_id,
            User.status == "active",
            Role.name.in_(role_names),
            (UserRole.expires_at.is_(None) | (UserRole.expires_at > now)),
        )
        .distinct()
        .order_by(User.id)
    )
    result = await db.execute(query)
    return {"data": [{"id": str(user_id)} for user_id in result.scalars().all()]}
