"""通知 API ルーター"""

from uuid import UUID

import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import (
    APIResponse,
    MetaInfo,
    NotificationListResponse,
    NotificationResponse,
    NotificationSendRequest,
    UnreadCountResponse,
)
from ..services.notification_service import (
    get_unread_count,
    get_user_notifications,
    mark_all_as_read,
    mark_as_read,
    create_notification_idempotent,
)
from ..config import get_settings
from ..services.neo_adapter import deliver_to_neo

router = APIRouter()


async def require_internal_api_key(
    x_internal_api_key: str | None = Header(default=None),
) -> None:
    configured_key = get_settings().INTERNAL_API_KEY
    if (
        not configured_key
        or not x_internal_api_key
        or not secrets.compare_digest(x_internal_api_key, configured_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INTERNAL_AUTH_REQUIRED",
                "message": "内部認証が必要です。",
            },
        )


def _api_response(data=None, meta=None, error=None, success=True):
    return APIResponse(success=success, data=data, error=error, meta=meta)


@router.post("/send", dependencies=[Depends(require_internal_api_key)])
async def send_notification(
    request: NotificationSendRequest,
    db: AsyncSession = Depends(get_db),
):
    notification, created = await create_notification_idempotent(
        db,
        recipient_id=request.recipient_id,
        template_code=request.template_code,
        template_vars=request.template_vars,
        metadata=request.metadata,
        idempotency_key=request.idempotency_key,
    )
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "TEMPLATE_NOT_FOUND",
                "message": "通知テンプレートが見つかりません。",
            },
        )
    neo_delivery = await deliver_to_neo(notification)
    if neo_delivery is True:
        notification.status = "sent"
        await db.flush()
    elif neo_delivery is False:
        notification.status = "failed"
        await db.flush()
    return _api_response(
        data=NotificationResponse.model_validate(notification).model_dump(),
        meta={"created": created, "neo_delivery": neo_delivery},
    )


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    category: str | None = Query(None),
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(token_data.sub)
    notifications, pmeta = await get_user_notifications(
        db,
        user_id=user_id,
        page=page,
        per_page=per_page,
        status=status_filter,
        category=category,
    )

    nlist = [NotificationResponse.model_validate(n) for n in notifications]
    result = NotificationListResponse(notifications=nlist, pagination=pmeta)

    meta = MetaInfo(
        page=pmeta.page,
        per_page=pmeta.per_page,
        total=pmeta.total,
        total_pages=pmeta.total_pages,
    )
    return _api_response(data=result.model_dump(), meta=meta)


@router.get("/unread-count")
async def unread_count(
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(token_data.sub)
    count = await get_unread_count(db, user_id=user_id)
    return _api_response(data=UnreadCountResponse(unread_count=count).model_dump())


@router.patch("/{notification_id}/read")
async def read_notification(
    notification_id: int,
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(token_data.sub)
    notification = await mark_as_read(
        db, notification_id=notification_id, user_id=user_id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "通知が見つかりません。"},
        )

    return _api_response(
        data=NotificationResponse.model_validate(notification).model_dump()
    )


@router.patch("/read-all")
async def read_all_notifications(
    token_data: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID(token_data.sub)
    count = await mark_all_as_read(db, user_id=user_id)
    return _api_response(data={"marked_read": count})
