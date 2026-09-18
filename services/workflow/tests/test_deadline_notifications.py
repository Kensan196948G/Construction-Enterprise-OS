import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.jobs.deadline_notifications import deadline_offset, notify_deadlines


def test_deadline_offset_handles_overdue_days():
    assert deadline_offset(date(2026, 9, 7), date(2026, 8, 31)) == 7
    assert deadline_offset(date(2026, 8, 30), date(2026, 8, 31)) == -1


def test_notify_deadlines_sends_for_active_statuses():
    due = MagicMock(
        id=uuid4(),
        title="月次報告",
        due_date=date(2026, 9, 7),
        submitted_by=uuid4(),
        status="pending_approval",
    )
    other = MagicMock(
        id=uuid4(),
        title="対象外",
        due_date=date(2026, 9, 8),
        submitted_by=uuid4(),
        status="processing",
    )
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [due, other]
    db.execute.return_value = result

    with patch(
        "src.jobs.deadline_notifications.resolve_notification_recipients",
        new=AsyncMock(return_value=[due.submitted_by]),
    ) as resolve, patch(
        "src.jobs.deadline_notifications.send_workflow_notifications",
        new=AsyncMock(return_value=1),
    ) as send:
        sent, skipped, failed = asyncio.run(notify_deadlines(db, date(2026, 8, 31)))

    assert sent == 1
    assert skipped == 1
    assert failed == 0
    send.assert_awaited_once()
    assert send.await_args.kwargs["transition"] == "deadline:7"
    resolve.assert_awaited_once()
