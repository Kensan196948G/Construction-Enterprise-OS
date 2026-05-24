"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
from uuid import UUID

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
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


class DocumentCreate(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(min_length=1, max_length=500)
    description: str | None = None
    document_type: str = Field(
        default="other",
        pattern="^(pdf|cad|bim|photo|video|spreadsheet|other)$",
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict | None = None


class DocumentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    tags: list[str] | None = None
    status: str | None = Field(
        default=None,
        pattern="^(draft|under_review|approved|rejected|obsolete|deleted)$",
    )


class DocumentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    name: str
    description: str | None
    document_type: str
    status: str
    current_version: int
    file_name: str
    file_size: int
    mime_type: str
    storage_key: str
    tags: list[str]
    metadata: dict | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    pagination: PaginationMeta


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    file_name: str
    file_size: int
    mime_type: str
    storage_key: str
    change_description: str | None
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentVersionListResponse(BaseModel):
    versions: list[DocumentVersionResponse]
    pagination: PaginationMeta


class VersionUploadRequest(BaseModel):
    change_description: str | None = None
