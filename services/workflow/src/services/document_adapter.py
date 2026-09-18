"""WorkflowからDocument Serviceの正本保存を呼び出す内部adapter。"""

import logging
import asyncio
from uuid import UUID

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


async def store_workflow_documents(
    *, document_ids: list[object], organization_id: UUID
) -> tuple[int, int]:
    settings = get_settings()
    if not settings.DOCUMENT_SERVICE_URL or not settings.DOCUMENT_INTERNAL_API_KEY:
        return 0, len(document_ids)

    stored = 0
    failed = 0
    attempts = max(1, settings.DOCUMENT_RETRY_COUNT + 1)
    async with httpx.AsyncClient(timeout=settings.NOTIFICATION_TIMEOUT_SECONDS) as client:
        for raw_id in document_ids:
            try:
                document_id = UUID(str(raw_id))
                url = f"{settings.DOCUMENT_SERVICE_URL.rstrip('/')}/api/v1/documents/internal/{document_id}/store-canonical"
                for attempt in range(attempts):
                    try:
                        response = await client.post(
                            url,
                            headers={
                                "X-Internal-API-Key": settings.DOCUMENT_INTERNAL_API_KEY,
                                "X-Organization-ID": str(organization_id),
                            },
                        )
                        response.raise_for_status()
                        stored += 1
                        break
                    except httpx.HTTPStatusError as exc:
                        retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
                        if not retryable or attempt == attempts - 1:
                            raise
                        await asyncio.sleep(2**attempt)
                    except httpx.RequestError:
                        if attempt == attempts - 1:
                            raise
                        await asyncio.sleep(2**attempt)
            except (ValueError, httpx.HTTPError):
                failed += 1
                logger.exception("Canonical document storage failed for %s", raw_id)
    return stored, failed


async def store_workflow_work_area(
    *, document_ids: list[object], organization_id: UUID, receipt_no: str
) -> tuple[int, int]:
    """提出済み添付を受付番号単位のOneDrive作業領域へ送る。"""
    settings = get_settings()
    if not settings.DOCUMENT_SERVICE_URL or not settings.DOCUMENT_INTERNAL_API_KEY:
        return 0, len(document_ids)

    stored = 0
    failed = 0
    attempts = max(1, settings.DOCUMENT_RETRY_COUNT + 1)
    async with httpx.AsyncClient(timeout=settings.NOTIFICATION_TIMEOUT_SECONDS) as client:
        for raw_id in document_ids:
            try:
                document_id = UUID(str(raw_id))
                url = f"{settings.DOCUMENT_SERVICE_URL.rstrip('/')}/api/v1/documents/internal/{document_id}/store-work-area"
                for attempt in range(attempts):
                    try:
                        response = await client.post(
                            url,
                            headers={
                                "X-Internal-API-Key": settings.DOCUMENT_INTERNAL_API_KEY,
                                "X-Organization-ID": str(organization_id),
                            },
                            data={"receipt_no": receipt_no},
                        )
                        response.raise_for_status()
                        stored += 1
                        break
                    except httpx.HTTPStatusError as exc:
                        retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
                        if not retryable or attempt == attempts - 1:
                            raise
                        await asyncio.sleep(2**attempt)
                    except httpx.RequestError:
                        if attempt == attempts - 1:
                            raise
                        await asyncio.sleep(2**attempt)
            except (ValueError, httpx.HTTPError):
                failed += 1
                logger.exception("Work area document storage failed for %s", raw_id)
    return stored, failed
