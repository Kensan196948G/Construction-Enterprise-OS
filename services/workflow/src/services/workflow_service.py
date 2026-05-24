"""ワークフロー実行エンジン"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import WorkflowApproval, WorkflowDefinition, WorkflowInstance


def _utcnow():
    return datetime.now(timezone.utc)


async def create_definition(
    db: AsyncSession,
    organization_id: UUID,
    name: str,
    description: str | None,
    category: str,
    steps: list[dict],
    created_by: UUID | None = None,
) -> WorkflowDefinition:
    definition = WorkflowDefinition(
        organization_id=organization_id,
        name=name,
        description=description,
        category=category,
        steps=steps,
        created_by=created_by,
    )
    db.add(definition)
    await db.flush()
    return definition


async def get_definitions(
    db: AsyncSession,
    organization_id: UUID | None = None,
    category: str | None = None,
    is_active: bool | None = None,
) -> list[WorkflowDefinition]:
    stmt = select(WorkflowDefinition)
    if organization_id:
        stmt = stmt.where(WorkflowDefinition.organization_id == organization_id)
    if category:
        stmt = stmt.where(WorkflowDefinition.category == category)
    if is_active is not None:
        stmt = stmt.where(WorkflowDefinition.is_active == is_active)
    stmt = stmt.order_by(WorkflowDefinition.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_definition_by_id(
    db: AsyncSession, definition_id: UUID
) -> WorkflowDefinition | None:
    stmt = select(WorkflowDefinition).where(WorkflowDefinition.id == definition_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def start_workflow(
    db: AsyncSession,
    definition_id: UUID,
    submitted_by: UUID,
    organization_id: UUID,
    title: str,
    description: str | None = None,
    priority: str = "normal",
    reference_type: str | None = None,
    reference_id: UUID | None = None,
    metadata: dict | None = None,
) -> WorkflowInstance:
    definition = await get_definition_by_id(db, definition_id)
    if not definition:
        raise ValueError(f"Workflow definition {definition_id} not found")

    instance = WorkflowInstance(
        definition_id=definition_id,
        organization_id=organization_id,
        title=title,
        description=description,
        category=definition.category,
        status="draft",
        priority=priority,
        reference_type=reference_type,
        reference_id=reference_id,
        metadata_=metadata or {},
        submitted_by=submitted_by,
    )
    db.add(instance)
    await db.flush()

    steps: list[dict] = definition.steps if isinstance(definition.steps, list) else []
    for step_data in sorted(steps, key=lambda s: s.get("order", 0)):
        approval = WorkflowApproval(
            instance_id=instance.id,
            step_order=step_data["order"],
            approver_role=step_data["role"],
            status="pending",
        )
        db.add(approval)

    await db.flush()
    return instance


async def submit_workflow(
    db: AsyncSession, instance_id: UUID, user_id: UUID
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status != "draft":
        raise ValueError(f"Workflow instance {instance_id} is not in draft status")
    if instance.submitted_by != user_id:
        raise ValueError("Only the submitter can submit the workflow")

    instance.status = "in_progress"
    instance.submitted_at = _utcnow()
    await db.flush()
    return instance


async def get_instances(
    db: AsyncSession,
    organization_id: UUID | None = None,
    status: str | None = None,
    category: str | None = None,
    submitted_by: UUID | None = None,
) -> list[WorkflowInstance]:
    stmt = select(WorkflowInstance).options(selectinload(WorkflowInstance.approvals))
    if organization_id:
        stmt = stmt.where(WorkflowInstance.organization_id == organization_id)
    if status:
        stmt = stmt.where(WorkflowInstance.status == status)
    if category:
        stmt = stmt.where(WorkflowInstance.category == category)
    if submitted_by:
        stmt = stmt.where(WorkflowInstance.submitted_by == submitted_by)
    stmt = stmt.order_by(WorkflowInstance.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_instance_with_chain(
    db: AsyncSession, instance_id: UUID
) -> WorkflowInstance | None:
    stmt = (
        select(WorkflowInstance)
        .options(selectinload(WorkflowInstance.approvals))
        .where(WorkflowInstance.id == instance_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_pending_approvals(
    db: AsyncSession, user_roles: list[str]
) -> list[WorkflowInstance]:
    if not user_roles:
        return []

    stmt = (
        select(WorkflowInstance)
        .options(selectinload(WorkflowInstance.approvals))
        .where(WorkflowInstance.status == "in_progress")
        .order_by(WorkflowInstance.created_at.desc())
    )
    result = await db.execute(stmt)
    instances = result.scalars().all()

    matching: list[WorkflowInstance] = []
    for instance in instances:
        current_approval = _get_current_approval(instance.approvals)
        if current_approval and _can_user_approve(current_approval, user_roles):
            matching.append(instance)
    return matching


async def cancel_workflow(
    db: AsyncSession, instance_id: UUID, user_id: UUID
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status in ("approved", "rejected", "cancelled"):
        raise ValueError(f"Workflow instance {instance_id} is already finalized")

    instance.status = "cancelled"
    await db.flush()
    return instance


def _get_current_approval(approvals: list[WorkflowApproval]) -> WorkflowApproval | None:
    sorted_approvals = sorted(approvals, key=lambda a: a.step_order)
    for approval in sorted_approvals:
        if approval.status == "pending":
            return approval
    return None


def _can_user_approve(approval: WorkflowApproval, user_roles: list[str]) -> bool:
    return approval.approver_role in user_roles
