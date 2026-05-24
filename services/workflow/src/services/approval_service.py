"""承認チェーン管理"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import WorkflowApproval, WorkflowInstance


def _utcnow():
    return datetime.now(timezone.utc)


def can_user_approve(approval: WorkflowApproval, user_roles: list[str]) -> bool:
    return approval.approver_role in user_roles


async def _get_approval(
    db: AsyncSession, instance_id: UUID, step_order: int
) -> WorkflowApproval | None:
    stmt = select(WorkflowApproval).where(
        WorkflowApproval.instance_id == instance_id,
        WorkflowApproval.step_order == step_order,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_instance(db: AsyncSession, instance_id: UUID) -> WorkflowInstance | None:
    from sqlalchemy.orm import selectinload

    stmt = (
        select(WorkflowInstance)
        .options(selectinload(WorkflowInstance.approvals))
        .where(WorkflowInstance.id == instance_id)
    )
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
) -> WorkflowInstance:
    instance = await _get_instance(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status != "in_progress":
        raise ValueError(f"Workflow instance {instance_id} is not in progress")

    approval = await _get_approval(db, instance_id, step_order)
    if not approval:
        raise ValueError(f"Approval step {step_order} not found for instance {instance_id}")
    if approval.status != "pending":
        raise ValueError(f"Approval step {step_order} is already {approval.status}")

    if user_roles and not can_user_approve(approval, user_roles):
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
        instance.status = "approved"
        instance.completed_at = _utcnow()

    await db.flush()
    return instance


async def reject_step(
    db: AsyncSession,
    instance_id: UUID,
    step_order: int,
    user_id: UUID,
    comment: str | None = None,
    user_roles: list[str] | None = None,
) -> WorkflowInstance:
    instance = await _get_instance(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status != "in_progress":
        raise ValueError(f"Workflow instance {instance_id} is not in progress")

    approval = await _get_approval(db, instance_id, step_order)
    if not approval:
        raise ValueError(f"Approval step {step_order} not found for instance {instance_id}")
    if approval.status != "pending":
        raise ValueError(f"Approval step {step_order} is already {approval.status}")

    if user_roles and not can_user_approve(approval, user_roles):
        raise ValueError(
            f"User does not have required role '{approval.approver_role}' "
            f"to reject step {step_order}"
        )

    approval.status = "rejected"
    approval.approver_id = user_id
    approval.comment = comment
    approval.approved_at = _utcnow()

    instance.status = "rejected"
    instance.completed_at = _utcnow()
    await db.flush()
    return instance
