"""通知作成・配信サービス"""

import logging
import math
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Notification, NotificationTemplate
from ..schemas import PaginationMeta
from .template_service import get_template_by_code, render_template

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    recipient_id: UUID,
    template_code: str,
    template_vars: dict | None = None,
    metadata: dict | None = None,
) -> Notification | None:
    template = await get_template_by_code(db, template_code)
    if not template:
        logger.warning("Template not found: %s", template_code)
        return None

    template_vars = template_vars or {}

    title = render_template(template.title_template, template_vars)
    body = render_template(template.body_template, template_vars)

    notification = Notification(
        template_id=template.id,
        recipient_id=recipient_id,
        title=title,
        body=body,
        metadata_=metadata or {},
        channels=template.channels,
        status="pending",
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def create_notification_idempotent(
    db: AsyncSession,
    recipient_id: UUID,
    template_code: str,
    template_vars: dict | None,
    metadata: dict | None,
    idempotency_key: str,
) -> tuple[Notification | None, bool]:
    """Create one notification per caller-supplied event key.

    The unique database index is the final concurrency guard. The initial lookup
    makes retries cheap and returns the already-created notification unchanged.
    """
    existing_result = await db.execute(
        select(Notification).where(Notification.idempotency_key == idempotency_key)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        return existing, False

    notification = await create_notification(
        db,
        recipient_id=recipient_id,
        template_code=template_code,
        template_vars=template_vars,
        metadata=metadata,
    )
    if notification is not None:
        notification.idempotency_key = idempotency_key
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            duplicate_result = await db.execute(
                select(Notification).where(
                    Notification.idempotency_key == idempotency_key
                )
            )
            duplicate = duplicate_result.scalar_one_or_none()
            if duplicate is None:
                raise
            return duplicate, False
    return notification, True


async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    category: str | None = None,
) -> tuple[list[Notification], PaginationMeta]:
    stmt = select(Notification).where(Notification.recipient_id == user_id)
    count_stmt = select(func.count(Notification.id)).where(
        Notification.recipient_id == user_id
    )

    if status:
        stmt = stmt.where(Notification.status == status)
        count_stmt = count_stmt.where(Notification.status == status)

    if category:
        stmt = stmt.join(Notification.template).where(
            NotificationTemplate.category == category
        )
        count_stmt = count_stmt.join(Notification.template).where(
            NotificationTemplate.category == category
        )

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    stmt = stmt.order_by(Notification.created_at.desc())
    stmt = stmt.offset(offset).limit(per_page)

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    meta = PaginationMeta(
        page=page, per_page=per_page, total=total, total_pages=total_pages
    )

    return list(notifications), meta


async def mark_as_read(
    db: AsyncSession, notification_id: int, user_id: UUID
) -> Notification | None:
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.recipient_id == user_id,
    )
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()

    if not notification:
        return None

    notification.status = "read"
    notification.read_at = func.now()
    await db.flush()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
    stmt = (
        update(Notification)
        .where(
            Notification.recipient_id == user_id,
            Notification.status == "sent",
        )
        .values(status="read", read_at=func.now())
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    stmt = select(func.count(Notification.id)).where(
        Notification.recipient_id == user_id,
        Notification.status == "sent",
    )
    result = await db.execute(stmt)
    return result.scalar() or 0
