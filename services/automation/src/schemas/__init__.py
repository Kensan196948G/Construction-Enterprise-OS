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
# Automation Rule
# ============================================
class RuleActionConfig(BaseModel):
    type: str = Field(min_length=1, max_length=50)
    config: dict = Field(default_factory=dict)


class RuleCreateRequest(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    trigger_type: str = Field(min_length=1, max_length=50)
    condition: dict = Field(default_factory=dict)
    action: RuleActionConfig
    is_active: bool = True


class RuleUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    trigger_type: str | None = None
    condition: dict | None = None
    action: RuleActionConfig | None = None
    is_active: bool | None = None


class RuleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    trigger_type: str
    condition: dict
    action: dict
    is_active: bool
    created_by: UUID | None
    last_triggered: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RuleListResponse(BaseModel):
    rules: list[RuleResponse]
    total: int


class RuleTestRequest(BaseModel):
    input_data: dict = Field(default_factory=dict)


class RuleTestResponse(BaseModel):
    rule_id: UUID
    rule_name: str
    matched: bool
    action_type: str
    action_result: dict


# ============================================
# Scheduled Task
# ============================================
class TaskCreateRequest(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    cron_expression: str = Field(min_length=1, max_length=100)
    action_type: str = Field(min_length=1, max_length=50)
    action_config: dict = Field(default_factory=dict)
    is_active: bool = True


class TaskUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    cron_expression: str | None = None
    action_type: str | None = None
    action_config: dict | None = None
    is_active: bool | None = None


class TaskResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    cron_expression: str
    action_type: str
    action_config: dict
    is_active: bool
    created_by: UUID | None
    last_run: datetime | None
    next_run: datetime | None
    last_status: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


class TaskRunResponse(BaseModel):
    id: UUID
    task_id: UUID
    organization_id: UUID
    status: str
    output_data: dict
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================
# Trigger
# ============================================
class TriggerCreateRequest(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    event_type: str = Field(min_length=1, max_length=100)
    filter_conditions: dict = Field(default_factory=dict)
    action_config: dict = Field(default_factory=dict)
    is_active: bool = True


class TriggerUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    event_type: str | None = None
    filter_conditions: dict | None = None
    action_config: dict | None = None
    is_active: bool | None = None


class TriggerResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    event_type: str
    filter_conditions: dict
    action_config: dict
    is_active: bool
    created_by: UUID | None
    last_triggered: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TriggerListResponse(BaseModel):
    triggers: list[TriggerResponse]
    total: int
