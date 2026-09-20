"""上流 CEOS サービスへ実際に接続する結合テスト

上流サービス（construction / erp）が起動していない場合はスキップする。
"""

import socket
from urllib.parse import urlparse

import pytest

from src.config import get_settings
from src.services.upstream import UpstreamClient
from tests.helpers import call_tool, initialize


def _tcp_reachable(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def _upstream_available() -> bool:
    settings = get_settings()
    return _tcp_reachable(settings.CONSTRUCTION_SERVICE_URL) and _tcp_reachable(
        settings.ERP_SERVICE_URL
    )


pytestmark = [
    pytest.mark.live_upstream,
    pytest.mark.skipif(
        not _upstream_available(),
        reason="CEOS 上流サービス（construction / erp）が起動していません",
    ),
]


async def test_live_upstream_health_endpoints():
    client = UpstreamClient(get_settings())
    try:
        construction = await client.get("construction", "/health")
        erp = await client.get("erp", "/health")
    finally:
        await client.aclose()
    assert construction.ok, construction.status_code
    assert erp.ok, erp.status_code


def test_live_mcp_tools_call_completes_round_trip(build_client, token):
    # 上流が起動していれば JSON-RPC 応答が返る（認可は上流判断のため isError でも可）
    client = build_client()
    initialize(client, token)
    result = call_tool(client, token, "ceos.ledger.get_summary", {})
    assert "result" in result
    assert "isError" in result["result"]
