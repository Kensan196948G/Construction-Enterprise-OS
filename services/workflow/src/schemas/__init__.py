"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================
# 共通
# ============================================
class APIResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    error: dict | None = None
    meta: dict | None = None


# ============================================
# ワークフロー定義
# ============================================
class WorkflowStepSchema(BaseModel):
    order: int
    role: str
    required: bool = True


class WorkflowDefinitionCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=50)
    steps: list[WorkflowStepSchema]


class WorkflowDefinitionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    category: str
    steps: list[WorkflowStepSchema]
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================
# ワークフローインスタンス
# ============================================
class WorkflowInstanceCreate(BaseModel):
    definition_id: UUID
    organization_id: UUID
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: str = "normal"
    reference_type: str | None = None
    reference_id: UUID | None = None
    metadata: dict = Field(default_factory=dict)


class WorkflowApprovalResponse(BaseModel):
    id: UUID
    instance_id: UUID
    step_order: int
    approver_id: UUID | None
    approver_role: str
    status: str
    comment: str | None
    approved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowInstanceResponse(BaseModel):
    id: UUID
    definition_id: UUID | None
    organization_id: UUID
    title: str
    description: str | None
    category: str
    status: str
    priority: str
    reference_type: str | None
    reference_id: UUID | None
    metadata: dict
    submitted_by: UUID
    submitted_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowInstanceDetailResponse(WorkflowInstanceResponse):
    approvals: list[WorkflowApprovalResponse] = Field(default_factory=list)


# ============================================
# 承認
# ============================================
class ApprovalAction(BaseModel):
    comment: str | None = None
