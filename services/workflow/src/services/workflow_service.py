"""ワークフロー実行エンジン"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import (
    WorkflowApproval,
    WorkflowAuditLog,
    WorkflowDefinition,
    WorkflowInquiry,
    WorkflowInstance,
    WorkflowStatusHistory,
)
from .check_service import SubmissionValidationError, validate_submission


_DUPLICATE_CANDIDATE_STATUSES = {
    "in_progress",
    "forwarded",
    "pending_approval",
    "processing",
    "approved",
    "completed",
    "stored",
}


def _utcnow():
    return datetime.now(timezone.utc)


async def _next_receipt_no(db: AsyncSession) -> str:
    year = _utcnow().year
    result = await db.execute(
        text(
            """
            INSERT INTO workflow.workflow_receipt_counters (receipt_year, next_value)
            VALUES (:receipt_year, 2)
            ON CONFLICT (receipt_year) DO UPDATE
                SET next_value = workflow.workflow_receipt_counters.next_value + 1
            RETURNING next_value - 1
            """
        ),
        {"receipt_year": year},
    )
    sequence = result.scalar_one()
    return f"SAW-{year}-{int(sequence):06d}"


def _calculate_due_date(
    metadata: dict | None, check_rules: dict | None, today: date | None = None
) -> date | None:
    """個別期限を優先し、未指定時は定義マスタの期限ルールを適用する。"""
    metadata = metadata or {}
    rules = check_rules or {}
    raw_deadline = metadata.get("deadline")
    if isinstance(raw_deadline, str):
        try:
            return date.fromisoformat(raw_deadline)
        except ValueError:
            pass

    rule = rules.get("deadline_rule")
    today = today or _utcnow().date()
    if isinstance(rule, str) and rule.startswith("DAYS:"):
        try:
            return today + timedelta(days=int(rule.split(":", 1)[1]))
        except (ValueError, TypeError):
            return None
    if isinstance(rule, str) and rule.startswith("MONTHLY_DAY:"):
        try:
            day = int(rule.split(":", 1)[1])
            if not 1 <= day <= 28:
                return None
            if today.day <= day:
                return today.replace(day=day)
            next_month = today.replace(day=28) + timedelta(days=4)
            return next_month.replace(day=day)
        except (ValueError, TypeError):
            return None
    return None


def _record_status_change(
    db: AsyncSession,
    instance: WorkflowInstance,
    from_status: str | None,
    to_status: str,
    changed_by: UUID,
    comment: str | None = None,
) -> None:
    history = WorkflowStatusHistory(
        instance_id=instance.id,
        from_status=from_status,
        to_status=to_status,
        changed_by=changed_by,
        comment=comment,
    )
    db.add(history)
    if "status_history" in instance.__dict__:
        instance.status_history.append(history)


def record_audit_log(
    db: AsyncSession,
    *,
    user_id: UUID | None,
    event_type: str,
    event_data: dict | None = None,
    success: bool = True,
) -> None:
    """Authの監査ログへ同一トランザクションで追記する。"""
    db.add(
        WorkflowAuditLog(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data or {},
            success=success,
        )
    )


def can_view_instance(
    instance: WorkflowInstance, user_id: UUID, user_roles: list[str]
) -> bool:
    """案件参照範囲を所有者・回付先・管理ロールに限定する。"""
    if {"admin", "management"}.intersection(user_roles):
        return True
    if instance.submitted_by == user_id:
        return True
    if any(approval.approver_id == user_id for approval in instance.approvals):
        return True
    if instance.status in {"forwarded", "pending_approval", "processing"}:
        return any(
            approval.status == "pending" and approval.approver_role in user_roles
            for approval in instance.approvals
        )
    return False


def _attachment_names(metadata: dict) -> set[str]:
    attachments = metadata.get("attachments", [])
    if not isinstance(attachments, list):
        return set()
    names: set[str] = set()
    for item in attachments:
        if isinstance(item, str) and item.strip():
            names.add(item.strip())
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            name = item["name"].strip()
            if name:
                names.add(name)
    return names


def _duplicate_score(candidate: WorkflowInstance, instance: WorkflowInstance) -> int | None:
    """共通キーで候補を絞り、仕様書の類似度スコアを算出する。"""
    current_metadata = instance.metadata_ if isinstance(instance.metadata_, dict) else {}
    candidate_metadata = (
        candidate.metadata_ if isinstance(candidate.metadata_, dict) else {}
    )
    current_code = current_metadata.get("construction_code")
    candidate_code = candidate_metadata.get("construction_code")
    current_doc_type = current_metadata.get("doc_type_code") or instance.category
    candidate_doc_type = candidate_metadata.get("doc_type_code") or candidate.category
    current_month = current_metadata.get("target_year_month")
    candidate_month = candidate_metadata.get("target_year_month")
    if not all(isinstance(value, str) and value for value in (
        current_code, candidate_code, current_doc_type, candidate_doc_type,
        current_month, candidate_month,
    )):
        return None
    if (current_code, current_doc_type, current_month) != (
        candidate_code, candidate_doc_type, candidate_month
    ):
        return None

    score = 2 if candidate.submitted_by == instance.submitted_by else 0
    current_amount = current_metadata.get("amount")
    candidate_amount = candidate_metadata.get("amount")
    if current_amount is not None and candidate_amount is not None and current_amount == candidate_amount:
        score += 1
    if _attachment_names(current_metadata) & _attachment_names(candidate_metadata):
        score += 1
    if isinstance(candidate.created_at, datetime) and isinstance(instance.created_at, datetime):
        if abs((candidate.created_at - instance.created_at).total_seconds()) <= 3 * 86400:
            score += 1
    return score


async def _find_duplicate_candidate(
    db: AsyncSession, instance: WorkflowInstance
) -> WorkflowInstance | None:
    result = await db.execute(
        select(WorkflowInstance).where(
            WorkflowInstance.organization_id == instance.organization_id,
            WorkflowInstance.id != instance.id,
            WorkflowInstance.status.in_(_DUPLICATE_CANDIDATE_STATUSES),
        )
    )
    for candidate in result.scalars().all():
        score = _duplicate_score(candidate, instance)
        if score is not None and score >= 3:
            return candidate
    return None


async def create_definition(
    db: AsyncSession,
    organization_id: UUID,
    name: str,
    description: str | None,
    category: str,
    steps: list[dict],
    check_rules: dict | None = None,
    created_by: UUID | None = None,
) -> WorkflowDefinition:
    definition = WorkflowDefinition(
        organization_id=organization_id,
        name=name,
        description=description,
        category=category,
        steps=steps,
        check_rules=check_rules or {},
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


async def update_definition(
    db: AsyncSession,
    definition_id: UUID,
    organization_id: UUID,
    values: dict,
) -> WorkflowDefinition:
    definition = await get_definition_by_id(db, definition_id)
    if not definition:
        raise ValueError(f"Workflow definition {definition_id} not found")
    if definition.organization_id != organization_id:
        raise ValueError("Workflow definition is not in the organization")
    for field, value in values.items():
        if value is not None:
            setattr(definition, field, value)
    await db.flush()
    return definition


async def create_inquiry(
    db: AsyncSession,
    instance_id: UUID,
    organization_id: UUID,
    asked_by: UUID,
    question: str,
    channel: str,
) -> WorkflowInquiry:
    instance = await get_instance_with_chain(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    inquiry = WorkflowInquiry(
        instance_id=instance_id,
        organization_id=organization_id,
        asked_by=asked_by,
        question=question,
        channel=channel,
    )
    db.add(inquiry)
    await db.flush()
    return inquiry


async def get_inquiries(
    db: AsyncSession, instance_id: UUID, organization_id: UUID
) -> list[WorkflowInquiry]:
    instance = await get_instance_with_chain(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    result = await db.execute(
        select(WorkflowInquiry)
        .where(
            WorkflowInquiry.instance_id == instance_id,
            WorkflowInquiry.organization_id == organization_id,
        )
        .order_by(WorkflowInquiry.created_at)
    )
    return list(result.scalars().all())


async def answer_inquiry(
    db: AsyncSession,
    inquiry_id: UUID,
    instance_id: UUID,
    organization_id: UUID,
    answered_by: UUID,
    answer: str,
) -> WorkflowInquiry:
    result = await db.execute(
        select(WorkflowInquiry).where(
            WorkflowInquiry.id == inquiry_id,
            WorkflowInquiry.instance_id == instance_id,
            WorkflowInquiry.organization_id == organization_id,
        )
    )
    inquiry = result.scalar_one_or_none()
    if not inquiry:
        raise ValueError(f"Workflow inquiry {inquiry_id} not found")
    if inquiry.status == "answered":
        raise ValueError("Workflow inquiry is already answered")
    inquiry.answer = answer
    inquiry.answered_by = answered_by
    inquiry.answered_at = _utcnow()
    inquiry.status = "answered"
    await db.flush()
    return inquiry


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
    if definition.organization_id != organization_id:
        raise ValueError(
            f"Workflow definition {definition_id} is not in the organization"
        )

    instance = WorkflowInstance(
        receipt_no=None,
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
        due_date=_calculate_due_date(metadata, definition.check_rules),
    )
    db.add(instance)
    await db.flush()
    _record_status_change(db, instance, None, "draft", submitted_by)

    steps: list[dict] = definition.steps if isinstance(definition.steps, list) else []
    for step_data in sorted(steps, key=lambda s: s.get("order", 0)):
        roles = step_data.get("roles") or [step_data["role"]]
        for role in dict.fromkeys(roles):
            approval = WorkflowApproval(
                instance_id=instance.id,
                step_order=step_data["order"],
                approver_role=role,
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

    definition = getattr(instance, "definition", None)
    if definition is not None:
        errors, warnings = validate_submission(
            instance.metadata_, definition.check_rules
        )
        if errors:
            raise SubmissionValidationError(errors, warnings)
        if warnings:
            instance.metadata_ = {**instance.metadata_, "check_warnings": warnings}

    duplicate = await _find_duplicate_candidate(db, instance)
    if duplicate is not None:
        instance.duplicate_flag = True
        duplicate_warning = {
            "field": "duplicate",
            "message": "同一工事・同一月の申請が既に登録されています。",
        }
        current_warnings = (
            instance.metadata_.get("check_warnings", [])
            if isinstance(instance.metadata_, dict)
            else []
        )
        if not isinstance(current_warnings, list):
            current_warnings = []
        instance.metadata_ = {
            **(instance.metadata_ if isinstance(instance.metadata_, dict) else {}),
            "check_warnings": [*current_warnings, duplicate_warning],
            "duplicate_candidate_receipt_no": duplicate.receipt_no,
        }

    # 受付番号は正式提出時にだけ発行し、下書きには仮番号を付与しない。
    if instance.receipt_no is None:
        instance.receipt_no = await _next_receipt_no(db)

    previous_status = instance.status
    instance.status = "in_progress"
    instance.submitted_at = _utcnow()
    _record_status_change(db, instance, previous_status, "in_progress", user_id)
    await db.flush()
    return instance


async def update_workflow_draft(
    db: AsyncSession,
    instance_id: UUID,
    user_id: UUID,
    title: str | None = None,
    description: str | None = None,
    metadata: dict | None = None,
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status != "draft":
        raise ValueError("Only a draft workflow can be edited")
    if instance.submitted_by != user_id:
        raise ValueError("Only the submitter can edit the workflow")

    if title is not None:
        instance.title = title
    if description is not None:
        instance.description = description
    if metadata is not None:
        instance.metadata_ = metadata
    await db.flush()
    return instance


async def resubmit_workflow(
    db: AsyncSession, instance_id: UUID, user_id: UUID
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status != "rejected":
        raise ValueError(f"Workflow instance {instance_id} is not rejected")
    if instance.submitted_by != user_id:
        raise ValueError("Only the submitter can resubmit the workflow")

    rejection_comment = next(
        (
            a.comment
            for a in reversed(instance.approvals)
            if a.status == "rejected" and a.comment
        ),
        None,
    )
    for approval in instance.approvals:
        approval.status = "pending"
        approval.approver_id = None
        approval.comment = None
        approval.approved_at = None

    instance.status = "in_progress"
    instance.submitted_at = _utcnow()
    instance.completed_at = None
    _record_status_change(
        db, instance, "rejected", "in_progress", user_id, rejection_comment
    )
    await db.flush()
    return instance


async def get_instances(
    db: AsyncSession,
    organization_id: UUID | None = None,
    status: str | None = None,
    category: str | None = None,
    submitted_by: UUID | None = None,
) -> list[WorkflowInstance]:
    stmt = select(WorkflowInstance).options(
        selectinload(WorkflowInstance.approvals),
        selectinload(WorkflowInstance.status_history),
    )
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
    db: AsyncSession, instance_id: UUID, organization_id: UUID | None = None
) -> WorkflowInstance | None:
    stmt = (
        select(WorkflowInstance)
        .options(
            selectinload(WorkflowInstance.approvals),
            selectinload(WorkflowInstance.status_history),
            selectinload(WorkflowInstance.definition),
        )
        .where(WorkflowInstance.id == instance_id)
    )
    if organization_id is not None:
        stmt = stmt.where(WorkflowInstance.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_instance_by_receipt(
    db: AsyncSession, receipt_no: str, organization_id: UUID | None = None
) -> WorkflowInstance | None:
    """受付番号を共通キーにした外部連携用の案件検索。"""
    stmt = (
        select(WorkflowInstance)
        .options(
            selectinload(WorkflowInstance.approvals),
            selectinload(WorkflowInstance.status_history),
            selectinload(WorkflowInstance.definition),
        )
        .where(WorkflowInstance.receipt_no == receipt_no)
    )
    if organization_id is not None:
        stmt = stmt.where(WorkflowInstance.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def transition_case(
    db: AsyncSession,
    instance_id: UUID,
    organization_id: UUID,
    changed_by: UUID,
    to_status: str,
    allowed_statuses: set[str],
    comment: str | None = None,
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    if instance.status not in allowed_statuses:
        raise ValueError(
            f"Workflow instance {instance_id} cannot transition from {instance.status}"
        )
    previous_status = instance.status
    instance.status = to_status
    if to_status == "rejected":
        instance.completed_at = _utcnow()
    if to_status == "stored":
        instance.canonical_stored_at = _utcnow()
        instance.canonical_error = None
    _record_status_change(db, instance, previous_status, to_status, changed_by, comment)
    await db.flush()
    return instance


async def judge_duplicate(
    db: AsyncSession,
    instance_id: UUID,
    organization_id: UUID,
    judged_by: UUID,
    decision: str,
    comment: str | None = None,
) -> WorkflowInstance:
    instance = await get_instance_with_chain(db, instance_id, organization_id)
    if not instance:
        raise ValueError(f"Workflow instance {instance_id} not found")
    instance.duplicate_flag = decision == "duplicate"
    metadata = instance.metadata_ if isinstance(instance.metadata_, dict) else {}
    instance.metadata_ = {
        **metadata,
        "duplicate_judgement": {
            "decision": decision,
            "comment": comment,
            "judged_by": str(judged_by),
            "judged_at": _utcnow().isoformat(),
        },
    }
    await db.flush()
    return instance


async def get_pending_approvals(
    db: AsyncSession, user_roles: list[str], organization_id: UUID | None = None
) -> list[WorkflowInstance]:
    if not user_roles:
        return []

    stmt = (
        select(WorkflowInstance)
        .options(selectinload(WorkflowInstance.approvals))
        .where(WorkflowInstance.status.in_(["in_progress", "pending_approval"]))
        .order_by(WorkflowInstance.created_at.desc())
    )
    if organization_id is not None:
        stmt = stmt.where(WorkflowInstance.organization_id == organization_id)
    result = await db.execute(stmt)
    instances = result.scalars().all()

    matching: list[WorkflowInstance] = []
    for instance in instances:
        current_approval = _get_current_approval(instance.approvals, user_roles)
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

    previous_status = instance.status
    instance.status = "cancelled"
    _record_status_change(db, instance, previous_status, "cancelled", user_id)
    await db.flush()
    return instance


def _get_current_approval(
    approvals: list[WorkflowApproval], user_roles: list[str] | None = None
) -> WorkflowApproval | None:
    sorted_approvals = sorted(approvals, key=lambda a: a.step_order)
    for approval in sorted_approvals:
        if approval.status == "pending" and (
            user_roles is None or approval.approver_role in user_roles
        ):
            return approval
    return None


def _can_user_approve(approval: WorkflowApproval, user_roles: list[str]) -> bool:
    return approval.approver_role in user_roles
