"""AI service OCR endpoint — returns OCR task list for the frontend dashboard."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..middleware.auth import get_current_user
from ..schemas import APIResponse

router = APIRouter()


class AiOcrTaskItem(BaseModel):
    id: str
    name: str
    doc_type: str
    status: str
    char_count: int
    processing_time: Optional[float]
    created_at: str
    confidence: Optional[float]


class AiOcrListResponse(BaseModel):
    tasks: List[AiOcrTaskItem]
    total: int


_MOCK_AI_OCR_TASKS = [
    AiOcrTaskItem(
        id="ai-ocr-001",
        name="工事請求書_2024-01.pdf",
        doc_type="invoice",
        status="completed",
        char_count=2480,
        processing_time=3.2,
        created_at="2024-01-15T09:00:00Z",
        confidence=0.97,
    ),
    AiOcrTaskItem(
        id="ai-ocr-002",
        name="橋梁設計図面_A棟.pdf",
        doc_type="drawing",
        status="completed",
        char_count=1890,
        processing_time=5.1,
        created_at="2024-01-16T10:30:00Z",
        confidence=0.93,
    ),
    AiOcrTaskItem(
        id="ai-ocr-003",
        name="工事仕様書_道路改良.pdf",
        doc_type="specification",
        status="processing",
        char_count=0,
        processing_time=None,
        created_at="2024-01-17T08:00:00Z",
        confidence=None,
    ),
    AiOcrTaskItem(
        id="ai-ocr-004",
        name="請負契約書_2024年度.pdf",
        doc_type="contract",
        status="completed",
        char_count=5320,
        processing_time=8.7,
        created_at="2024-01-18T14:00:00Z",
        confidence=0.99,
    ),
    AiOcrTaskItem(
        id="ai-ocr-005",
        name="施工管理報告書_Q1.pdf",
        doc_type="report",
        status="failed",
        char_count=0,
        processing_time=None,
        created_at="2024-01-19T11:00:00Z",
        confidence=None,
    ),
    AiOcrTaskItem(
        id="ai-ocr-006",
        name="安全点検仕様書_2024.pdf",
        doc_type="specification",
        status="queued",
        char_count=0,
        processing_time=None,
        created_at="2024-01-20T09:30:00Z",
        confidence=None,
    ),
]


@router.get("")
async def list_ai_ocr_tasks(
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    _current_user=Depends(get_current_user),
):
    """List OCR tasks processed by the AI service."""
    start = (page - 1) * per_page
    end = start + per_page
    tasks = _MOCK_AI_OCR_TASKS[start:end]
    return APIResponse(
        data=AiOcrListResponse(tasks=tasks, total=len(_MOCK_AI_OCR_TASKS)).model_dump()
    )
