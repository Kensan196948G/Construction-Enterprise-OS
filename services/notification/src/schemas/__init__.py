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


class NotificationResponse(BaseModel):
    id: int
    template_id: UUID | None
    recipient_id: UUID
    title: str
    body: str
    metadata: dict | None = None
    channels: list[str]
    status: str
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    pagination: PaginationMeta


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationTemplateCreate(BaseModel):
    code: str = Field(max_length=100)
    name: str = Field(max_length=255)
    channels: list[str] = Field(default=["in_app", "email"])
    title_template: str
    body_template: str
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    category: str = Field(max_length=50)


class NotificationTemplateUpdate(BaseModel):
    name: str | None = None
    channels: list[str] | None = None
    title_template: str | None = None
    body_template: str | None = None
    priority: str | None = Field(default=None, pattern="^(low|normal|high|urgent)$")
    category: str | None = None


class NotificationTemplateResponse(BaseModel):
    id: UUID
    code: str
    name: str
    channels: list[str]
    title_template: str
    body_template: str
    priority: str
    category: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationTemplateListResponse(BaseModel):
    templates: list[NotificationTemplateResponse]
    pagination: PaginationMeta
