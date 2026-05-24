"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class APIResponse[T](BaseModel):
    success: bool = True
    data: T | None = None
    error: "ErrorDetail | None" = None
    meta: "MetaInfo | None" = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class MetaInfo(BaseModel):
    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    total_pages: int | None = None


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class PromptTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=50)
    system_prompt: str
    user_prompt_template: str
    model: str = "gpt-4"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=32000)


class PromptTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    system_prompt: str | None = None
    user_prompt_template: str | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=32000)
    is_active: bool | None = None


class PromptTemplateResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    category: str
    system_prompt: str
    user_prompt_template: str
    model: str
    temperature: float
    max_tokens: int
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateListResponse(BaseModel):
    templates: list[PromptTemplateResponse]
    pagination: PaginationMeta


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    prompt_template_id: UUID | None = None
    conversation_id: UUID | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=32000)
    variables: dict | None = None


class ChatResponse(BaseModel):
    message: ChatMessage
    conversation_id: UUID | None = None
    usage: dict | None = None


class CompletionRequest(BaseModel):
    prompt_template_id: UUID
    variables: dict = Field(default_factory=dict)
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=32000)


class CompletionResponse(BaseModel):
    content: str
    prompt_template_id: UUID
    usage: dict | None = None


class EmbeddingRequest(BaseModel):
    source_type: str
    source_id: UUID
    content: str
    metadata: dict | None = None
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class EmbeddingSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    source_type: str | None = None
    filters: dict | None = None


class EmbeddingSearchResult(BaseModel):
    id: UUID
    source_type: str
    source_id: UUID
    chunk_index: int
    content: str
    similarity: float
    metadata: dict | None


class EmbeddingSearchResponse(BaseModel):
    results: list[EmbeddingSearchResult]


class RAGSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    source_type: str | None = None
    filters: dict | None = None


class RAGGenerateRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    source_type: str | None = None
    filters: dict | None = None
    prompt_template_id: UUID | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=32000)


class RAGGenerateResponse(BaseModel):
    answer: str
    sources: list[EmbeddingSearchResult]
    usage: dict | None = None
