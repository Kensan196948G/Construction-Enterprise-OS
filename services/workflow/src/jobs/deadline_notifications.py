"""期限通知ジョブ。Schedulerから内部API経由で呼び出す。"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import WorkflowInstance
from ..services.notification_adapter import (
    resolve_notification_recipients,
    send_workflow_notifications,
)

DEADLINE_OFFSETS = {7, 3, 1, 0, -1}
DEADLINE_CANDIDATE_STATUSES = {
    "in_progress",
    "forwarded",
    "pending_approval",
    "processing",
}


def deadline_offset(due_date: date, today: date) -> int:
    return (due_date - today).days


async def notify_deadlines(
    db: AsyncSession, today: date | None = None
) -> tuple[int, int, int]:
    today = today or date.today()
    result = await db.execute(
        select(WorkflowInstance).where(
            WorkflowInstance.status.in_(DEADLINE_CANDIDATE_STATUSES),
            WorkflowInstance.due_date.is_not(None),
        )
    )
    candidates = list(result.scalars().all())
    sent = 0
    skipped = 0
    failed = 0
    for instance in candidates:
        if instance.due_date is None:
            skipped += 1
            continue
        offset = deadline_offset(instance.due_date, today)
        if offset not in DEADLINE_OFFSETS:
            skipped += 1
            continue
        recipients = await resolve_notification_recipients(
            organization_id=instance.organization_id,
            roles={"management", "admin"},
            fallback=instance.submitted_by,
        )
        delivered = await send_workflow_notifications(
            recipient_ids=recipients,
            template_code="workflow.deadline",
            instance_id=instance.id,
            transition=f"deadline:{offset}",
            actor_id=instance.submitted_by,
            template_vars={
                "document_name": instance.title,
                "deadline": instance.due_date.isoformat(),
                "days_remaining": offset,
            },
        )
        if delivered:
            sent += delivered
        else:
            failed += 1
    return sent, skipped, failed
