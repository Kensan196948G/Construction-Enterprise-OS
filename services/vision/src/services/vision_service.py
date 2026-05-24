"""Vision service layer for OCR, image analysis, and vector DB operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ImageAnalysis, OCRResult, VectorIndex


def _utcnow():
    return datetime.now(timezone.utc)


# ── OCR ──

async def create_ocr_result(
    db: AsyncSession,
    organization_id: UUID,
    extracted_text: str,
    document_id: UUID | None = None,
    file_key: str | None = None,
    language: str = "ja",
    confidence: float | None = None,
    page_count: int | None = None,
    processing_time_ms: int | None = None,
    entities: dict | None = None,
    status: str = "completed",
    error_message: str | None = None,
    processed_by: str | None = None,
) -> OCRResult:
    ocr = OCRResult(
        organization_id=organization_id,
        document_id=document_id,
        file_key=file_key,
        language=language,
        extracted_text=extracted_text,
        confidence=confidence,
        page_count=page_count,
        processing_time_ms=processing_time_ms,
        entities=entities or {},
        status=status,
        error_message=error_message,
        processed_by=processed_by,
    )
    db.add(ocr)
    await db.flush()
    return ocr


async def get_ocr_results(
    db: AsyncSession,
    organization_id: UUID | None = None,
    status: str | None = None,
    document_id: UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[OCRResult]:
    stmt = select(OCRResult)
    if organization_id:
        stmt = stmt.where(OCRResult.organization_id == organization_id)
    if status:
        stmt = stmt.where(OCRResult.status == status)
    if document_id:
        stmt = stmt.where(OCRResult.document_id == document_id)
    stmt = stmt.order_by(OCRResult.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_ocr_result_by_id(
    db: AsyncSession, result_id: UUID
) -> OCRResult | None:
    stmt = select(OCRResult).where(OCRResult.id == result_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ── Image Analysis ──

async def create_image_analysis(
    db: AsyncSession,
    organization_id: UUID,
    file_key: str,
    analysis_type: str,
    results: dict,
    confidence: float | None = None,
    processing_time_ms: int | None = None,
    model_used: str | None = None,
    status: str = "completed",
) -> ImageAnalysis:
    analysis = ImageAnalysis(
        organization_id=organization_id,
        file_key=file_key,
        analysis_type=analysis_type,
        results=results,
        confidence=confidence,
        processing_time_ms=processing_time_ms,
        model_used=model_used,
        status=status,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def get_image_analyses(
    db: AsyncSession,
    organization_id: UUID | None = None,
    analysis_type: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ImageAnalysis]:
    stmt = select(ImageAnalysis)
    if organization_id:
        stmt = stmt.where(ImageAnalysis.organization_id == organization_id)
    if analysis_type:
        stmt = stmt.where(ImageAnalysis.analysis_type == analysis_type)
    if status:
        stmt = stmt.where(ImageAnalysis.status == status)
    stmt = stmt.order_by(ImageAnalysis.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_image_analysis_by_id(
    db: AsyncSession, analysis_id: UUID
) -> ImageAnalysis | None:
    stmt = select(ImageAnalysis).where(ImageAnalysis.id == analysis_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ── Vector Indices ──

async def create_vector_index(
    db: AsyncSession,
    organization_id: UUID,
    collection_name: str,
    dimension: int,
    index_type: str = "ivfflat",
    metric: str = "cosine",
) -> VectorIndex:
    vi = VectorIndex(
        organization_id=organization_id,
        collection_name=collection_name,
        dimension=dimension,
        index_type=index_type,
        metric=metric,
    )
    db.add(vi)
    await db.flush()
    return vi


async def get_vector_indices(
    db: AsyncSession,
    organization_id: UUID | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[VectorIndex]:
    stmt = select(VectorIndex)
    if organization_id:
        stmt = stmt.where(VectorIndex.organization_id == organization_id)
    if is_active is not None:
        stmt = stmt.where(VectorIndex.is_active == is_active)
    stmt = stmt.order_by(VectorIndex.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_vector_index_by_id(
    db: AsyncSession, index_id: UUID
) -> VectorIndex | None:
    stmt = select(VectorIndex).where(VectorIndex.id == index_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_vector_index(
    db: AsyncSession,
    index_id: UUID,
    is_active: bool | None = None,
    document_count: int | None = None,
    total_vectors: int | None = None,
) -> VectorIndex | None:
    vi = await get_vector_index_by_id(db, index_id)
    if not vi:
        return None
    if is_active is not None:
        vi.is_active = is_active
    if document_count is not None:
        vi.document_count = document_count
    if total_vectors is not None:
        vi.total_vectors = total_vectors
    await db.flush()
    return vi


async def delete_vector_index(
    db: AsyncSession, index_id: UUID
) -> bool:
    stmt = delete(VectorIndex).where(VectorIndex.id == index_id)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def increment_vector_counts(
    db: AsyncSession, index_id: UUID, added_docs: int, added_vectors: int
) -> VectorIndex | None:
    vi = await get_vector_index_by_id(db, index_id)
    if not vi:
        return None
    vi.document_count += added_docs
    vi.total_vectors += added_vectors
    await db.flush()
    return vi
