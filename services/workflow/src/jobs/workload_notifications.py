"""地域別の処理量を集計し、負荷超過時に管理部へ通知するジョブ。"""

from collections import defaultdict
from datetime import date, datetime, timezone
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import WorkflowInstance
from ..services.notification_adapter import (
    resolve_notification_recipients,
    send_workflow_notifications,
)


def _region(instance: WorkflowInstance) -> str:
    metadata = instance.metadata_ if isinstance(instance.metadata_, dict) else {}
    return str(metadata.get("region") or metadata.get("branch") or "unknown")


def _month_delta(year: int, month: int, delta: int) -> tuple[int, int]:
    value = year * 12 + month - 1 + delta
    return value // 12, value % 12 + 1


async def notify_workload_alerts(
    db: AsyncSession, today: date | None = None
) -> tuple[int, int]:
    today = today or date.today()
    settings = get_settings()
    threshold = settings.WORKLOAD_ALERT_RATIO
    # 当月比較には直近12か月分の実績があれば十分なため、無制限の全件取得を避ける。
    start_year, start_month = _month_delta(today.year, today.month, -12)
    window_start = datetime(start_year, start_month, 1, tzinfo=timezone.utc)
    result = await db.execute(
        select(WorkflowInstance).where(WorkflowInstance.created_at >= window_start)
    )
    instances = list(result.scalars().all())
    counts: defaultdict[tuple[UUID, str, int, int], int] = defaultdict(int)
    for instance in instances:
        created_at = getattr(instance, "created_at", None)
        if created_at is None:
            continue
        counts[
            (
                instance.organization_id,
                _region(instance),
                created_at.year,
                created_at.month,
            )
        ] += 1

    sent = 0
    skipped = 0
    # counts はこの後 history 参照で新規キーが挿入されるため、反復前にキーを固定する。
    for organization_id, region, year, month in list(counts):
        if (year, month) != (today.year, today.month):
            continue
        current = counts[(organization_id, region, year, month)]
        history = [
            counts[(organization_id, region, *_month_delta(year, month, -offset))]
            for offset in range(1, 13)
        ]
        baseline = sum(history) / len(history)
        if baseline <= 0 or current < baseline * threshold:
            skipped += 1
            continue
        recommended_staff = max(
            1,
            int(
                (current - baseline + settings.WORKLOAD_CAPACITY_PER_STAFF - 1)
                // settings.WORKLOAD_CAPACITY_PER_STAFF
            ),
        )
        recipients = await resolve_notification_recipients(
            organization_id=organization_id, roles={"management", "admin"}
        )
        variables = {
            "region": region,
            "normal_avg": round(baseline, 1),
            "current": current,
            "ratio": round(current / baseline * 100, 1),
            "recommend_staff": recommended_staff,
        }
        event_id = uuid5(
            NAMESPACE_URL,
            f"workflow-load:{organization_id}:{region}:{today.isoformat()}",
        )
        sent += await send_workflow_notifications(
            recipient_ids=recipients,
            template_code="workflow.load_alert",
            instance_id=event_id,
            transition=f"load:{today.isoformat()}:{region}",
            actor_id=organization_id,
            template_vars=variables,
        )
        sent += await send_workflow_notifications(
            recipient_ids=recipients,
            template_code="workflow.support_request",
            instance_id=event_id,
            transition=f"support:{today.isoformat()}:{region}",
            actor_id=organization_id,
            template_vars=variables,
        )
    return sent, skipped
