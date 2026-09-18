"""承認チェーン管理"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import WorkflowApproval, WorkflowInstance
from .workflow_service import _record_status_change


def _utcnow():
    return datetime.now(timezone.utc)


def can_user_approve(approval: WorkflowApproval, user_roles: list[str]) -> bool:
    return approval.approver_role in user_roles


async def _get_approval(
    db: AsyncSession,
    instance_id: UUID,
    step_order: int,
    user_roles: list[str],
) -> WorkflowApproval | None:
    stmt = select(WorkflowApproval).where(
        WorkflowApproval.instance_id == instance_id,
        WorkflowApproval.step_order == step_order,
        WorkflowApproval.status == "pending",
        WorkflowApproval.approver_role.in_(user_roles),
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def _get_instance(db: AsyncSession, instance_id: UUID) -> WorkflowInstance | None:
    from sqlalchemy.orm import selectinload

    stmt = (
        select(WorkflowInstance)
        .options(
            selectinload(WorkflowInstance.approvals),
            selectinload(WorkflowInstance.status_history),
        )
        .where(WorkflowInstance.id == instance_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_scoped_instance(
    db: AsyncSession, instance_id: UUID, organization_id: UUID | None
) -> WorkflowInstance | None:
    from sqlalchemy.orm import selectinload

    stmt = (
        select(WorkflowInstance)
        .options(
            selectinload(WorkflowInstance.approvals),
            selectinload(WorkflowInstance.status_history),
        )
        .where(WorkflowInstance.id == instance_id)
    )
    if organization_id is not None:
        stmt = stmt.where(WorkflowInstance.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _get_current_step_order(approvals: list[WorkflowApproval]) -> int | None:
    sorted_approvals = sorted(approvals, key=lambda a: a.step_order)
    for approval in sorted_approvals:
        if approval.status == "pending":
            return approval.step_order
    return None


async def approve_step(
    db: AsyncSession,
    instance_id: UUID,
    step_order: int,
    user_id: UUID,
    comment: str | None = None,
    user_roles: list[str] | None = None,
    organization_id: UUID | None = None,
) -> WorkflowInstance:
    instance = await _get_scoped_instance(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status not in {"in_progress", "pending_approval"}:
        raise ValueError(f"Workflow instance {instance_id} is not in progress")

    approval = await _get_approval(db, instance_id, step_order, user_roles or [])
    if not approval:
        raise ValueError(
            f"Approval step {step_order} not found for instance {instance_id}"
        )
    if approval.status != "pending":
        raise ValueError(f"Approval step {step_order} is already {approval.status}")

    current_step_order = _get_current_step_order(instance.approvals)
    if current_step_order != step_order:
        raise ValueError(
            f"Approval step {step_order} is not the current step "
            f"(expected {current_step_order})"
        )

    if not can_user_approve(approval, user_roles or []):
        raise ValueError(
            f"User does not have required role '{approval.approver_role}' "
            f"to approve step {step_order}"
        )

    approval.status = "approved"
    approval.approver_id = user_id
    approval.comment = comment
    approval.approved_at = _utcnow()
    await db.flush()

    sorted_approvals = sorted(instance.approvals, key=lambda a: a.step_order)
    pending_count = sum(1 for a in sorted_approvals if a.status == "pending")

    if pending_count == 0:
        previous_status = instance.status
        instance.status = "approved"
        instance.completed_at = _utcnow()
        _record_status_change(db, instance, previous_status, "approved", user_id)

    await db.flush()
    return instance


async def reject_step(
    db: AsyncSession,
    instance_id: UUID,
    step_order: int,
    user_id: UUID,
    comment: str | None = None,
    user_roles: list[str] | None = None,
    organization_id: UUID | None = None,
) -> WorkflowInstance:
    instance = await _get_scoped_instance(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status not in {"in_progress", "pending_approval"}:
        raise ValueError(f"Workflow instance {instance_id} is not in progress")

    approval = await _get_approval(db, instance_id, step_order, user_roles or [])
    if not approval:
        raise ValueError(
            f"Approval step {step_order} not found for instance {instance_id}"
        )
    if approval.status != "pending":
        raise ValueError(f"Approval step {step_order} is already {approval.status}")

    current_step_order = _get_current_step_order(instance.approvals)
    if current_step_order != step_order:
        raise ValueError(
            f"Approval step {step_order} is not the current step "
            f"(expected {current_step_order})"
        )

    if not can_user_approve(approval, user_roles or []):
        raise ValueError(
            f"User does not have required role '{approval.approver_role}' "
            f"to reject step {step_order}"
        )

    approval.status = "rejected"
    approval.approver_id = user_id
    approval.comment = comment
    approval.approved_at = _utcnow()

    previous_status = instance.status
    instance.status = "rejected"
    instance.completed_at = _utcnow()
    _record_status_change(db, instance, previous_status, "rejected", user_id, comment)
    await db.flush()
    return instance
