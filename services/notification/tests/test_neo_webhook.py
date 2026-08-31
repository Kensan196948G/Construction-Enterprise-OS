import hashlib
import hmac
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request

from src.api.webhooks import NeoNotificationCallback, neo_callback


def _request(body: bytes) -> Request:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "path": "/"}, receive)


@pytest.mark.asyncio
async def test_neo_callback_updates_read_state_and_metadata():
    notification = MagicMock(
        id=7,
        metadata_={"source": "workflow"},
        status="pending",
        read_at=None,
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = notification
    db = AsyncMock()
    db.execute.return_value = result
    db.flush = AsyncMock()
    occurred_at = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
    payload = NeoNotificationCallback(
        notification_id=7,
        idempotency_key="event-1",
        event="responded",
        response="確認しました",
        occurred_at=occurred_at,
    )
    body = json.dumps(payload.model_dump(mode="json"), separators=(",", ":")).encode()
    signature = hmac.new(b"secret", body, hashlib.sha256).hexdigest()

    with patch(
        "src.api.webhooks.get_settings",
        return_value=SimpleNamespace(NEO_WEBHOOK_SECRET="secret"),
    ):
        response = await neo_callback(
            _request(body),
            payload,
            x_neo_signature=signature,
            db=db,
        )

    assert response == {
        "success": True,
        "notification_id": 7,
        "workflow_reflected": None,
    }
    assert notification.status == "read"
    assert notification.read_at == occurred_at
    assert notification.metadata_["neo_callback"]["response"] == "確認しました"
    db.flush.assert_awaited_once()
