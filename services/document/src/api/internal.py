"""Workflowサービス等からの内部呼び出し専用API。

X-Internal-API-Key による fail-closed 認証を必須とし、
X-Organization-ID によるテナント境界チェックを行う。

正本保存・作業領域保存は「要求を記録する」だけでなく、MinIO 上の実体ファイルを
保存先（CANONICAL_STORAGE_ROOT または OneDrive）へ実際に転送する。転送に
失敗した場合は 5xx を返し、Workflow 側のリトライと業務エラー表示に委ねる
（成功したように見せかけない）。
"""

import logging
import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import Document
from ..models.base import get_db
from ..schemas import APIResponse
from ..services import canonical_storage, document_service

logger = logging.getLogger(__name__)

router = APIRouter()

# storage_error 系カラム(Text)へ入れる最大長。異常に長い例外文字列での肥大を防ぐ。
_MAX_STORAGE_ERROR_LENGTH = 1000


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


async def _persist_storage_failure(
    db: AsyncSession, document: Document, field: str, exc
) -> None:
    """転送失敗を DB へ記録してから 5xx を返すための確定処理。

    例外を送出すると get_db 依存がロールバックするため、ここで明示的に
    コミットして失敗記録を残す。操作ごとのカラムに記録するので、後続の
    別操作が成功しても失敗の記録は失われない。
    """
    setattr(document, field, f"{exc.code}: {exc.message}"[:_MAX_STORAGE_ERROR_LENGTH])
    await db.commit()


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
    try:
        result = await canonical_storage.store_canonical(document)
    except canonical_storage.StorageTransferError as exc:
        logger.warning(
            "Canonical storage failed: document=%s code=%s", document_id, exc.code
        )
        await _persist_storage_failure(db, document, "canonical_storage_error", exc)
        raise HTTPException(status_code=exc.status_code, detail=exc.as_detail()) from exc

    document.canonical_stored_at = datetime.now(timezone.utc)
    document.canonical_path = result.relative_path
    document.canonical_storage_backend = result.backend
    document.canonical_storage_error = None
    await db.flush()
    return _api_response(
        data={
            "document_id": str(document.id),
            "stored": True,
            "backend": result.backend,
            "path": result.relative_path,
            "size_bytes": result.size_bytes,
        }
    )


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
    try:
        result = await canonical_storage.store_work_area(document, receipt_no)
    except canonical_storage.StorageTransferError as exc:
        logger.warning(
            "Work area storage failed: document=%s code=%s", document_id, exc.code
        )
        await _persist_storage_failure(db, document, "work_area_storage_error", exc)
        raise HTTPException(status_code=exc.status_code, detail=exc.as_detail()) from exc

    document.work_area_receipt_no = receipt_no
    document.work_area_stored_at = datetime.now(timezone.utc)
    document.work_area_path = result.relative_path
    document.work_area_storage_backend = result.backend
    document.work_area_storage_error = None
    await db.flush()
    return _api_response(
        data={
            "document_id": str(document.id),
            "stored": True,
            "backend": result.backend,
            "path": result.relative_path,
            "size_bytes": result.size_bytes,
        }
    )
