"""API request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Common ──

class APIResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    error: dict | None = None
    meta: dict | None = None


# ── OCR ──

class OCRProcessRequest(BaseModel):
    organization_id: UUID
    document_id: UUID | None = None
    file_key: str | None = Field(None, max_length=1000)
    language: str = Field("ja", max_length=10)


class OCREntities(BaseModel):
    dates: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    names: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)


class OCRResultResponse(BaseModel):
    id: UUID
    organization_id: UUID
    document_id: UUID | None
    file_key: str | None
    language: str
    extracted_text: str
    confidence: float | None
    page_count: int | None
    processing_time_ms: int | None
    entities: dict
    status: str
    error_message: str | None
    processed_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Image Analysis ──

class ImageAnalyzeRequest(BaseModel):
    organization_id: UUID
    file_key: str = Field(min_length=1, max_length=1000)
    analysis_type: str = Field(min_length=1, max_length=50)


class ImageAnalysisResponse(BaseModel):
    id: UUID
    organization_id: UUID
    file_key: str
    analysis_type: str
    results: dict
    confidence: float | None
    processing_time_ms: int | None
    model_used: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Vector DB ──

class VectorIndexCreate(BaseModel):
    organization_id: UUID
    collection_name: str = Field(min_length=1, max_length=255)
    dimension: int = Field(gt=0)
    index_type: str = Field("ivfflat", max_length=50)
    metric: str = Field("cosine", max_length=20)


class VectorIndexUpdate(BaseModel):
    is_active: bool | None = None


class VectorIndexResponse(BaseModel):
    id: UUID
    organization_id: UUID
    collection_name: str
    dimension: int
    index_type: str
    metric: str
    document_count: int
    total_vectors: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VectorSearchRequest(BaseModel):
    index_id: UUID
    query_text: str = Field(min_length=1)
    top_k: int = Field(5, ge=1, le=100)


class VectorSearchResult(BaseModel):
    source_id: str
    source_type: str
    chunk_index: int
    content: str
    similarity: float
    metadata: dict


class VectorIndexRequest(BaseModel):
    index_id: UUID
    documents: list["VectorDocumentInput"]


class VectorDocumentInput(BaseModel):
    source_id: UUID
    source_type: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)
    metadata: dict = Field(default_factory=dict)
