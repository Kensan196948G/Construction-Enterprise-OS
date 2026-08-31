"""API リクエスト/レスポンス スキーマ"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


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
    order: int = Field(gt=0)
    role: str | None = Field(default=None, min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=list)
    required: bool = True

    @model_validator(mode="after")
    def validate_roles(self):
        roles = [role.strip() for role in self.roles if role.strip()]
        if self.role:
            roles.insert(0, self.role)
        if not roles:
            raise ValueError("workflow step requires role or roles")
        self.roles = list(dict.fromkeys(roles))
        self.role = self.roles[0]
        return self


class WorkflowDefinitionCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=50)
    steps: list[WorkflowStepSchema] = Field(min_length=1)
    check_rules: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_step_order(self):
        orders = [step.order for step in self.steps]
        if len(orders) != len(set(orders)):
            raise ValueError("workflow step orders must be unique")
        return self


class WorkflowDefinitionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    steps: list[WorkflowStepSchema] | None = Field(default=None, min_length=1)
    check_rules: dict[str, Any] | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_step_order(self):
        if self.steps is not None:
            orders = [step.order for step in self.steps]
            if len(orders) != len(set(orders)):
                raise ValueError("workflow step orders must be unique")
        return self


class WorkflowDefinitionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    category: str
    steps: list[WorkflowStepSchema]
    check_rules: dict[str, Any]
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


class WorkflowInstanceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    metadata: dict | None = None


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


class WorkflowInquiryCreate(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    channel: str = Field(default="system", pattern="^(phone|email|system)$")


class WorkflowInquiryAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)


class CaseAction(BaseModel):
    comment: str | None = Field(default=None, max_length=5000)


class DuplicateJudgement(BaseModel):
    decision: str = Field(pattern="^(regular|duplicate|recheck)$")
    comment: str | None = Field(default=None, max_length=5000)


class WorkflowInquiryResponse(BaseModel):
    id: UUID
    instance_id: UUID
    organization_id: UUID
    question: str
    answer: str | None
    channel: str
    status: str
    asked_by: UUID
    answered_by: UUID | None
    created_at: datetime
    answered_at: datetime | None

    model_config = {"from_attributes": True}
