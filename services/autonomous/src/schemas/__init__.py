"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
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
# Autonomous Agent
# ============================================
class AgentCreateRequest(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    agent_type: str = Field(min_length=1, max_length=50)
    target_resource: str | None = None
    config: dict = Field(default_factory=dict)
    is_enabled: bool = True


class AgentUpdateRequest(BaseModel):
    name: str | None = None
    agent_type: str | None = None
    target_resource: str | None = None
    config: dict | None = None
    is_enabled: bool | None = None


class AgentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    agent_type: str
    status: str
    target_resource: str | None
    config: dict
    last_run_at: datetime | None
    run_count: int
    error_count: int
    is_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int


# ============================================
# Digital Twin
# ============================================
class TwinCreateRequest(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    name: str = Field(min_length=1, max_length=500)
    twin_type: str = Field(min_length=1, max_length=50)
    bim_model_id: UUID | None = None
    iot_device_ids: list[UUID] = Field(default_factory=list)
    sync_interval_seconds: int = Field(default=60, ge=1, le=86400)
    data_sources: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class TwinUpdateRequest(BaseModel):
    name: str | None = None
    project_id: UUID | None = None
    bim_model_id: UUID | None = None
    iot_device_ids: list[UUID] | None = None
    sync_interval_seconds: int | None = None
    data_sources: dict | None = None
    metadata: dict | None = None


class TwinSyncRequest(BaseModel):
    current_state: dict = Field(default_factory=dict)


class TwinResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    name: str
    twin_type: str
    status: str
    bim_model_id: UUID | None
    iot_device_ids: list
    last_sync_at: datetime | None
    sync_interval_seconds: int
    data_sources: dict
    current_state: dict
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TwinCurrentStateResponse(BaseModel):
    twin_id: UUID
    name: str
    status: str
    current_state: dict
    last_sync_at: datetime | None


class TwinListResponse(BaseModel):
    twins: list[TwinResponse]
    total: int


# ============================================
# Autonomous Task
# ============================================
class TaskCreateRequest(BaseModel):
    organization_id: UUID
    agent_id: UUID | None = None
    digital_twin_id: UUID | None = None
    title: str = Field(min_length=1, max_length=500)
    task_type: str = Field(min_length=1, max_length=50)
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    input_data: dict | None = None


class TaskResponse(BaseModel):
    id: UUID
    organization_id: UUID
    agent_id: UUID | None
    digital_twin_id: UUID | None
    title: str
    task_type: str
    priority: str
    status: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


# ============================================
# Construction Simulation
# ============================================
class SimulationCreateRequest(BaseModel):
    organization_id: UUID
    project_id: UUID | None = None
    digital_twin_id: UUID | None = None
    name: str = Field(min_length=1, max_length=500)
    simulation_type: str = Field(min_length=1, max_length=50)
    parameters: dict = Field(default_factory=dict)
    created_by: UUID | None = None


class SimulationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    digital_twin_id: UUID | None
    name: str
    simulation_type: str
    status: str
    parameters: dict
    results: dict
    progress_percent: float
    started_at: datetime | None
    completed_at: datetime | None
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SimulationListResponse(BaseModel):
    simulations: list[SimulationResponse]
    total: int
