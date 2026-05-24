"""Platform API リクエスト・レスポンス スキーマ"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================
# 共通
# ============================================
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


# ============================================
# Viewer Config
# ============================================
class ViewerConfigCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(max_length=255)
    viewer_type: str = Field(max_length=50)
    model_ids: list[UUID] = Field(default_factory=list)
    layer_ids: list[UUID] = Field(default_factory=list)
    camera_state: dict[str, Any] = Field(default_factory=dict)
    visible_categories: list[str] = Field(default_factory=list)
    clipping_planes: dict[str, Any] = Field(default_factory=dict)
    theme: str = Field(default="light", max_length=20)


class ViewerConfigUpdate(BaseModel):
    model_config = {"protected_namespaces": ()}

    name: str | None = Field(default=None, max_length=255)
    viewer_type: str | None = Field(default=None, max_length=50)
    model_ids: list[UUID] | None = None
    layer_ids: list[UUID] | None = None
    camera_state: dict[str, Any] | None = None
    visible_categories: list[str] | None = None
    clipping_planes: dict[str, Any] | None = None
    theme: str | None = Field(default=None, max_length=20)


class ViewerConfigResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: UUID
    organization_id: UUID
    project_id: UUID | None = None
    name: str
    viewer_type: str
    model_ids: list[UUID] = Field(default_factory=list)
    layer_ids: list[UUID] = Field(default_factory=list)
    camera_state: dict[str, Any] = Field(default_factory=dict)
    visible_categories: list[str] = Field(default_factory=list)
    clipping_planes: dict[str, Any] = Field(default_factory=dict)
    theme: str = "light"
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime


class ViewerConfigWithScenesResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: UUID
    organization_id: UUID
    project_id: UUID | None = None
    name: str
    viewer_type: str
    model_ids: list[UUID] = Field(default_factory=list)
    layer_ids: list[UUID] = Field(default_factory=list)
    camera_state: dict[str, Any] = Field(default_factory=dict)
    visible_categories: list[str] = Field(default_factory=list)
    clipping_planes: dict[str, Any] = Field(default_factory=dict)
    theme: str = "light"
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    scenes: list["ViewerSceneResponse"] = Field(default_factory=list)


# ============================================
# Viewer Scene
# ============================================
class ViewerSceneCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None
    camera_state: dict[str, Any]
    annotations: list[dict[str, Any]] = Field(default_factory=list)
    measurements: list[dict[str, Any]] = Field(default_factory=list)


class ViewerSceneResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: UUID
    config_id: UUID
    name: str
    description: str | None = None
    camera_state: dict[str, Any]
    annotations: list[dict[str, Any]] = Field(default_factory=list)
    measurements: list[dict[str, Any]] = Field(default_factory=list)
    created_by: UUID | None = None
    created_at: datetime


# ============================================
# IoT Dashboard
# ============================================
class IoTDashboardCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(max_length=255)
    description: str | None = None
    layout: dict[str, Any]
    refresh_interval_seconds: int = Field(default=10, ge=1)
    is_public: bool = False


class IoTDashboardUpdate(BaseModel):
    model_config = {"protected_namespaces": ()}

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    layout: dict[str, Any] | None = None
    refresh_interval_seconds: int | None = Field(default=None, ge=1)
    is_public: bool | None = None


class IoTDashboardResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: UUID
    organization_id: UUID
    project_id: UUID | None = None
    name: str
    description: str | None = None
    layout: dict[str, Any]
    refresh_interval_seconds: int = 10
    is_public: bool = False
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime


# ============================================
# Device Group
# ============================================
class DeviceGroupCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    organization_id: UUID
    name: str = Field(max_length=255)
    description: str | None = None
    device_ids: list[UUID] = Field(default_factory=list)
    group_type: str | None = Field(default=None, max_length=50)
    parent_group_id: UUID | None = None


class DeviceGroupUpdate(BaseModel):
    model_config = {"protected_namespaces": ()}

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    device_ids: list[UUID] | None = None
    group_type: str | None = Field(default=None, max_length=50)
    parent_group_id: UUID | None = None


class DeviceGroupResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    device_ids: list[UUID] = Field(default_factory=list)
    group_type: str | None = None
    parent_group_id: UUID | None = None
    created_at: datetime
