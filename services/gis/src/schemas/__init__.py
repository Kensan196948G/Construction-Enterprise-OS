"""GeoJSON / API リクエスト・レスポンス スキーマ"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================
# 共通
# ============================================
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


# ============================================
# GeoJSON Geometry
# ============================================
class GeoJSONGeometry(BaseModel):
    type: str  # Point / Polygon / LineString / MultiPoint
    coordinates: Any  # 型はジオメトリによって異なる


# ============================================
# GeoJSON Feature
# ============================================
class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list)


# ============================================
# 工事現場 (Construction Site)
# ============================================
class SiteCreate(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(max_length=500)
    site_code: str | None = Field(default=None, max_length=100)
    location: GeoJSONGeometry  # Point
    work_area: GeoJSONGeometry | None = None  # Polygon
    site_type: str | None = Field(default=None, max_length=50)
    status: str = Field(default="active", max_length=20)
    address: str | None = Field(default=None, max_length=500)
    elevation: float | None = None
    area_sqm: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SiteUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=500)
    site_code: str | None = Field(default=None, max_length=100)
    location: GeoJSONGeometry | None = None
    work_area: GeoJSONGeometry | None = None
    site_type: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    elevation: float | None = None
    area_sqm: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] | None = None


class SiteResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None = None
    name: str
    site_code: str | None = None
    site_type: str | None = None
    status: str
    address: str | None = None
    elevation: float | None = None
    area_sqm: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] | None = None
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SiteGeoJSONResponse(GeoJSONFeature):
    pass


# ============================================
# インフラ設備 (Infrastructure)
# ============================================
class InfrastructureCreate(BaseModel):
    organization_id: UUID
    name: str = Field(max_length=500)
    infra_type: str = Field(max_length=50)
    location: GeoJSONGeometry  # Point
    line_geom: GeoJSONGeometry | None = None  # LineString
    status: str = Field(default="active", max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InfrastructureUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=500)
    infra_type: str | None = Field(default=None, max_length=50)
    location: GeoJSONGeometry | None = None
    line_geom: GeoJSONGeometry | None = None
    status: str | None = Field(default=None, max_length=20)
    metadata: dict[str, Any] | None = None


class InfrastructureResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    infra_type: str
    status: str
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InfrastructureGeoJSONResponse(GeoJSONFeature):
    pass


# ============================================
# 災害危険区域 (Hazard Zone)
# ============================================
class HazardZoneCreate(BaseModel):
    organization_id: UUID
    name: str = Field(max_length=500)
    hazard_type: str = Field(max_length=50)
    zone_area: GeoJSONGeometry  # Polygon
    risk_level: str = Field(default="medium", max_length=20)
    description: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HazardZoneUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=500)
    hazard_type: str | None = Field(default=None, max_length=50)
    zone_area: GeoJSONGeometry | None = None
    risk_level: str | None = Field(default=None, max_length=20)
    description: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    metadata: dict[str, Any] | None = None


class HazardZoneResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    hazard_type: str
    risk_level: str
    description: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HazardZoneGeoJSONResponse(GeoJSONFeature):
    pass


# ============================================
# Nearby Search
# ============================================
class NearbyQuery(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_m: float = Field(gt=0, default=1000)


class BoundingBoxQuery(BaseModel):
    min_lat: float = Field(ge=-90, le=90)
    min_lng: float = Field(ge=-180, le=180)
    max_lat: float = Field(ge=-90, le=90)
    max_lng: float = Field(ge=-180, le=180)
