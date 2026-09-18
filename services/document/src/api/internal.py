"""Workflowサービス等からの内部呼び出し専用API。

X-Internal-API-Key による fail-closed 認証を必須とし、
X-Organization-ID によるテナント境界チェックを行う。
"""

import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import Document
from ..models.base import get_db
from ..schemas import APIResponse
from ..services import document_service

router = APIRouter()


def _api_response(data=None, meta=None, error=None, success=True):
    return APIResponse(success=success, data=data, error=error, meta=meta)


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


async def _get_authorized_document(
    db: AsyncSession, document_id: UUID, x_organization_id: str | None
) -> Document:
    document = await document_service.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "文書が見つかりません。"},
        )

    try:
        organization_id = UUID(x_organization_id) if x_organization_id else None
    except ValueError:
        organization_id = None

    if organization_id is None or organization_id != document.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ORGANIZATION_MISMATCH",
                "message": "組織が一致しないため操作できません。",
            },
        )

    return document


@router.post(
    "/{document_id}/store-canonical",
    dependencies=[Depends(require_internal_api_key)],
)
async def store_canonical(
    document_id: UUID,
    x_organization_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    document = await _get_authorized_document(db, document_id, x_organization_id)
    document.canonical_stored_at = datetime.now(timezone.utc)
    await db.flush()
    return _api_response(data={"document_id": str(document.id), "stored": True})


@router.post(
    "/{document_id}/store-work-area",
    dependencies=[Depends(require_internal_api_key)],
)
async def store_work_area(
    document_id: UUID,
    receipt_no: str = Form(..., max_length=30),
    x_organization_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    document = await _get_authorized_document(db, document_id, x_organization_id)
    document.work_area_receipt_no = receipt_no
    document.work_area_stored_at = datetime.now(timezone.utc)
    await db.flush()
    return _api_response(data={"document_id": str(document.id), "stored": True})
