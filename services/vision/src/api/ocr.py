"""OCR processing API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import APIResponse, OCRProcessRequest
from ..services import vision_service

router = APIRouter()


def _ocr_to_response(ocr) -> dict:
    return {
        "id": str(ocr.id),
        "organization_id": str(ocr.organization_id),
        "document_id": str(ocr.document_id) if ocr.document_id else None,
        "file_key": ocr.file_key,
        "language": ocr.language,
        "extracted_text": ocr.extracted_text,
        "confidence": ocr.confidence,
        "page_count": ocr.page_count,
        "processing_time_ms": ocr.processing_time_ms,
        "entities": ocr.entities,
        "status": ocr.status,
        "error_message": ocr.error_message,
        "processed_by": ocr.processed_by,
        "created_at": ocr.created_at.isoformat() if ocr.created_at else None,
    }


@router.post("/ocr/process", status_code=status.HTTP_201_CREATED)
async def process_ocr(
    body: OCRProcessRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    ocr = await vision_service.create_ocr_result(
        db,
        organization_id=body.organization_id,
        document_id=body.document_id,
        file_key=body.file_key,
        language=body.language,
        extracted_text="",
        status="pending",
    )
    return APIResponse(data=_ocr_to_response(ocr))


@router.get("/ocr/results")
async def list_ocr_results(
    organization_id: UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    document_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    results = await vision_service.get_ocr_results(
        db,
        organization_id=organization_id,
        status=status_filter,
        document_id=document_id,
        skip=skip,
        limit=limit,
    )
    return APIResponse(data=[_ocr_to_response(r) for r in results])


@router.get("/ocr/results/{result_id}")
async def get_ocr_result(
    result_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    ocr = await vision_service.get_ocr_result_by_id(db, result_id)
    if not ocr:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "OCR result not found."},
        )
    return APIResponse(data=_ocr_to_response(ocr))
