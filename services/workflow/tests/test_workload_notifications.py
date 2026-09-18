import asyncio
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.jobs.workload_notifications import notify_workload_alerts


def _instance(organization_id, created_at, count=1):
    instances = []
    for _ in range(count):
        instances.append(
            MagicMock(
                organization_id=organization_id,
                created_at=created_at,
                metadata_={"region": "関東"},
            )
        )
    return instances


def test_notify_workload_alerts_sends_load_and_support_notifications():
    organization_id = uuid4()
    instances = _instance(
        organization_id, datetime(2026, 8, 10, tzinfo=timezone.utc), count=30
    )
    for month in range(1, 8):
        instances.extend(
            _instance(
                organization_id,
                datetime(2026, month, 10, tzinfo=timezone.utc),
                count=10,
            )
        )
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = instances
    db.execute.return_value = result
    settings = MagicMock(WORKLOAD_ALERT_RATIO=1.5, WORKLOAD_CAPACITY_PER_STAFF=20)

    with patch(
        "src.jobs.workload_notifications.get_settings", return_value=settings
    ), patch(
        "src.jobs.workload_notifications.resolve_notification_recipients",
        new=AsyncMock(return_value=[uuid4(), uuid4()]),
    ), patch(
        "src.jobs.workload_notifications.send_workflow_notifications",
        new=AsyncMock(return_value=2),
    ) as send:
        sent, skipped = asyncio.run(
            notify_workload_alerts(db, today=date(2026, 8, 31))
        )

    assert sent == 4
    assert skipped == 0
    assert send.await_count == 2
    assert {
        call.kwargs["template_code"] for call in send.await_args_list
    } == {"workflow.load_alert", "workflow.support_request"}
