"""OCR processing API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..middleware.auth import TokenData, get_current_user
from ..models.base import get_db
from ..schemas import APIResponse, OCRProcessRequest
from ..services import vision_service

router = APIRouter()


class OcrTaskItem(BaseModel):
    id: str
    name: str
    doc_type: str
    status: str
    char_count: int
    processing_time: Optional[float]
    created_at: str
    confidence: Optional[float]


class OcrTaskListResponse(BaseModel):
    tasks: List[OcrTaskItem]
    total: int


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


_MOCK_OCR_TASKS = [
    OcrTaskItem(
        id="ocr-task-001",
        name="工事請求書_2024-01.pdf",
        doc_type="invoice",
        status="completed",
        char_count=2480,
        processing_time=3.2,
        created_at="2024-01-15T09:00:00Z",
        confidence=0.97,
    ),
    OcrTaskItem(
        id="ocr-task-002",
        name="橋梁設計図面_A棟.pdf",
        doc_type="drawing",
        status="completed",
        char_count=1890,
        processing_time=5.1,
        created_at="2024-01-16T10:30:00Z",
        confidence=0.93,
    ),
    OcrTaskItem(
        id="ocr-task-003",
        name="工事仕様書_道路改良.pdf",
        doc_type="specification",
        status="processing",
        char_count=0,
        processing_time=None,
        created_at="2024-01-17T08:00:00Z",
        confidence=None,
    ),
    OcrTaskItem(
        id="ocr-task-004",
        name="請負契約書_2024年度.pdf",
        doc_type="contract",
        status="completed",
        char_count=5320,
        processing_time=8.7,
        created_at="2024-01-18T14:00:00Z",
        confidence=0.99,
    ),
    OcrTaskItem(
        id="ocr-task-005",
        name="施工管理報告書_Q1.pdf",
        doc_type="report",
        status="failed",
        char_count=0,
        processing_time=None,
        created_at="2024-01-19T11:00:00Z",
        confidence=None,
    ),
    OcrTaskItem(
        id="ocr-task-006",
        name="安全点検仕様書_2024.pdf",
        doc_type="specification",
        status="queued",
        char_count=0,
        processing_time=None,
        created_at="2024-01-20T09:30:00Z",
        confidence=None,
    ),
]


@router.get("/vision/ocr/tasks")
async def list_ocr_tasks(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    current_user: TokenData = Depends(get_current_user),
):
    """OCR task list endpoint for frontend dashboard."""
    start = (page - 1) * per_page
    end = start + per_page
    tasks = _MOCK_OCR_TASKS[start:end]
    return APIResponse(
        data=OcrTaskListResponse(tasks=tasks, total=len(_MOCK_OCR_TASKS)).model_dump()
    )
