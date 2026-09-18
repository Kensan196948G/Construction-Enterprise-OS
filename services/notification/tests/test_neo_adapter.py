from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.services.neo_adapter import deliver_to_neo


@pytest.mark.asyncio
async def test_neo_delivery_is_fail_closed_when_not_configured():
    notification = SimpleNamespace(channels=["neo"])
    settings = SimpleNamespace(NEO_ENABLED=False, NEO_API_URL="", NEO_API_KEY="")
    with patch("src.services.neo_adapter.get_settings", return_value=settings):
        assert await deliver_to_neo(notification) is None


@pytest.mark.asyncio
async def test_neo_delivery_fails_when_enabled_without_endpoint():
    notification = SimpleNamespace(channels=["neo"])
    settings = SimpleNamespace(NEO_ENABLED=True, NEO_API_URL="", NEO_API_KEY="")
    with patch("src.services.neo_adapter.get_settings", return_value=settings):
        assert await deliver_to_neo(notification) is False


@pytest.mark.asyncio
async def test_neo_delivery_sends_contract_payload_and_authentication():
    recipient_id = uuid4()
    notification = SimpleNamespace(
        channels=["in_app", "neo"],
        recipient_id=recipient_id,
        title="件名",
        body="本文",
        metadata_={"source": "workflow"},
        idempotency_key="event-1",
    )
    settings = SimpleNamespace(
        NEO_ENABLED=True,
        NEO_API_URL="https://neo.example.invalid/api/notifications",
        NEO_API_KEY="test-key",
        NEO_TIMEOUT_SECONDS=5.0,
    )
    response = MagicMock()
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = False
    client.post.return_value = response

    with patch("src.services.neo_adapter.get_settings", return_value=settings), patch(
        "src.services.neo_adapter.httpx.AsyncClient", return_value=client
    ):
        assert await deliver_to_neo(notification) is True

    client.post.assert_awaited_once_with(
        settings.NEO_API_URL,
        json={
            "recipient_id": str(recipient_id),
            "subject": "件名",
            "body": "本文",
            "metadata": {"source": "workflow"},
            "idempotency_key": "event-1",
        },
        headers={
            "Authorization": "Bearer test-key",
            "Idempotency-Key": "event-1",
        },
    )
