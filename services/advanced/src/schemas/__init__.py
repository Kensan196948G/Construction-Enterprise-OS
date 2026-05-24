"""API リクエスト/レスポンス スキーマ"""

from datetime import date, datetime
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
# 港湾施工管理 (Marine Construction)
# ============================================
class MarineConstructionCreateRequest(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(min_length=1, max_length=500)
    construction_type: str = Field(min_length=1, max_length=50)
    water_depth: float | None = None
    tide_info: dict | None = None
    wave_condition: dict | None = None
    equipment_deployed: list[str] | None = None
    material_volume: float | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    supervisor_id: UUID | None = None


class MarineConstructionUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=500)
    construction_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)
    water_depth: float | None = None
    tide_info: dict | None = None
    wave_condition: dict | None = None
    equipment_deployed: list[str] | None = None
    material_volume: float | None = None
    progress_percent: float | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    supervisor_id: UUID | None = None


class ProgressUpdateRequest(BaseModel):
    progress_percent: float = Field(ge=0, le=100)


class MarineConstructionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    name: str
    construction_type: str
    status: str
    water_depth: float | None
    tide_info: dict | None
    wave_condition: dict | None
    equipment_deployed: list[str] | None
    material_volume: float | None
    progress_percent: float | None
    location: str | None
    start_date: date | None
    end_date: date | None
    supervisor_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================
# 点検AI (Inspection Records)
# ============================================
class InspectionRecordCreateRequest(BaseModel):
    organization_id: UUID
    asset_name: str = Field(min_length=1, max_length=500)
    asset_type: str = Field(min_length=1, max_length=50)
    inspection_method: str | None = Field(None, max_length=50)
    ai_model_used: str | None = Field(None, max_length=100)
    defect_type: str | None = Field(None, max_length=50)
    severity: str | None = Field(None, max_length=20)
    confidence: float | None = None
    defect_count: int | None = None
    location: str | None = None
    image_keys: list[str] | None = None
    ai_analysis: dict | None = None
    inspector_id: UUID | None = None
    inspection_date: date
    requires_action: bool = False


class InspectionRecordUpdateRequest(BaseModel):
    asset_name: str | None = Field(None, max_length=500)
    asset_type: str | None = Field(None, max_length=50)
    inspection_method: str | None = Field(None, max_length=50)
    ai_model_used: str | None = Field(None, max_length=100)
    defect_type: str | None = Field(None, max_length=50)
    severity: str | None = Field(None, max_length=20)
    confidence: float | None = None
    defect_count: int | None = None
    location: str | None = None
    image_keys: list[str] | None = None
    ai_analysis: dict | None = None
    inspector_id: UUID | None = None
    inspection_date: date | None = None
    requires_action: bool | None = None


class DefectSummaryResponse(BaseModel):
    total_inspections: int
    by_severity: dict[str, int]
    by_asset_type: dict[str, int]
    by_defect_type: dict[str, int]
    requires_action_count: int
    average_confidence: float | None


class InspectionRecordResponse(BaseModel):
    id: UUID
    organization_id: UUID
    asset_name: str
    asset_type: str
    inspection_method: str | None
    ai_model_used: str | None
    defect_type: str | None
    severity: str | None
    confidence: float | None
    defect_count: int | None
    location: str | None
    image_keys: list[str] | None
    ai_analysis: dict | None
    inspector_id: UUID | None
    inspection_date: date
    requires_action: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================
# AI設計照査 (Design Review)
# ============================================
class DesignReviewCreateRequest(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    design_document_id: UUID | None = None
    review_type: str = Field(min_length=1, max_length=50)
    ai_suggestions: list[dict] | None = None
    compliance_checks: dict | None = None
    reviewer_id: UUID | None = None


class DesignReviewUpdateRequest(BaseModel):
    review_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)
    ai_suggestions: list[dict] | None = None
    compliance_checks: dict | None = None
    reviewer_id: UUID | None = None


class ComplianceReportResponse(BaseModel):
    review_id: UUID
    review_type: str
    status: str
    standards_checked: list[str]
    passed_count: int
    failed_count: int
    violations: list[dict]
    suggestions: list[dict]


class DesignReviewResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    design_document_id: UUID | None
    review_type: str
    status: str
    ai_suggestions: list[dict] | None
    compliance_checks: dict | None
    reviewer_id: UUID | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================
# 予知保全 (Predictive Models)
# ============================================
class PredictiveModelCreateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    organization_id: UUID
    asset_name: str = Field(min_length=1, max_length=500)
    asset_type: str = Field(min_length=1, max_length=50)
    model_type: str = Field(min_length=1, max_length=50)
    training_data_count: int | None = None
    accuracy: float | None = None
    failure_probability: float | None = Field(None, ge=0, le=1)
    remaining_life_days: int | None = None
    recommendations: list[dict] | None = None
    input_metrics: dict | None = None
    next_maintenance_predicted: date | None = None


class PredictiveModelUpdateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    asset_name: str | None = Field(None, max_length=500)
    asset_type: str | None = Field(None, max_length=50)
    model_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)
    training_data_count: int | None = None
    accuracy: float | None = None
    failure_probability: float | None = Field(None, ge=0, le=1)
    remaining_life_days: int | None = None
    recommendations: list[dict] | None = None
    input_metrics: dict | None = None
    next_maintenance_predicted: date | None = None


class PredictionResultResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_id: UUID
    asset_name: str
    asset_type: str
    model_type: str
    status: str
    failure_probability: float | None
    remaining_life_days: int | None
    next_maintenance_predicted: date | None
    recommendations: list[dict] | None


class PredictiveModelResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: UUID
    organization_id: UUID
    asset_name: str
    asset_type: str
    model_type: str
    status: str
    training_data_count: int | None
    accuracy: float | None
    last_trained_at: datetime | None
    next_maintenance_predicted: date | None
    failure_probability: float | None
    remaining_life_days: int | None
    recommendations: list[dict] | None
    input_metrics: dict | None
    created_at: datetime
    updated_at: datetime
