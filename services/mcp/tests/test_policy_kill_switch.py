"""キルスイッチ・許可リストのテスト（ネットワーク非依存）

fail-closed: 無効化・未許可・未登録はすべて拒否される。
"""

import pytest

from src.config import Settings
from src.tools import (
    REGISTRY,
    RESULT_SERVER_DISABLED,
    RESULT_TOOL_NOT_ALLOWED,
    RESULT_TOOL_NOT_FOUND,
    execute_tool,
    is_server_enabled,
    is_tool_allowed,
    load_registry,
)
from tests.helpers import FakeUpstreamClient, call_tool, initialize, mcp_headers


@pytest.fixture(autouse=True)
def _loaded_registry():
    load_registry()


def _settings(**kwargs) -> Settings:
    return Settings(**kwargs)


def test_server_disabled_by_kill_switch():
    assert is_server_enabled(_settings(MCP_ENABLED=False)) is False
    assert is_server_enabled(_settings(MCP_ENABLED=True)) is True


def test_empty_allowlist_allows_registered_tools_only():
    settings = _settings(MCP_TOOL_ALLOWLIST="")
    for name in REGISTRY.names:
        assert is_tool_allowed(name, REGISTRY, settings) is True
    assert is_tool_allowed("ceos.unknown.tool", REGISTRY, settings) is False


def test_allowlist_restricts_to_listed_tools():
    settings = _settings(MCP_TOOL_ALLOWLIST="ceos.wbs.get_tree")
    assert is_tool_allowed("ceos.wbs.get_tree", REGISTRY, settings) is True
    assert is_tool_allowed("ceos.ledger.get_summary", REGISTRY, settings) is False


def test_allowlist_with_unknown_or_empty_entry_fails_closed():
    settings = _settings(MCP_TOOL_ALLOWLIST="ceos.unknown.tool")
    for name in REGISTRY.names:
        assert is_tool_allowed(name, REGISTRY, settings) is False


async def test_execute_tool_refused_when_server_disabled():
    outcome = await execute_tool(
        "ceos.wbs.get_tree",
        {"project_id": "00000000-0000-0000-0000-000000000001"},
        authorization="Bearer x",
        client=FakeUpstreamClient(),
        registry=REGISTRY,
        settings=_settings(MCP_ENABLED=False),
    )
    assert outcome.result_code == RESULT_SERVER_DISABLED
    assert outcome.is_error is True


async def test_execute_tool_refused_when_not_allowlisted():
    settings = _settings(MCP_TOOL_ALLOWLIST="ceos.contract.list")
    outcome = await execute_tool(
        "ceos.wbs.get_tree",
        {"project_id": "00000000-0000-0000-0000-000000000001"},
        authorization="Bearer x",
        client=FakeUpstreamClient(),
        registry=REGISTRY,
        settings=settings,
    )
    assert outcome.result_code == RESULT_TOOL_NOT_ALLOWED


async def test_execute_tool_refused_when_unknown():
    outcome = await execute_tool(
        "ceos.unknown.tool",
        {},
        authorization="Bearer x",
        client=FakeUpstreamClient(),
        registry=REGISTRY,
        settings=_settings(),
    )
    assert outcome.result_code == RESULT_TOOL_NOT_FOUND


def test_http_server_disabled_returns_503(build_client, token):
    client = build_client(enabled=False)
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers=mcp_headers(token),
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MCP_DISABLED"


def test_http_allowlist_hides_and_blocks_other_tools(build_client, token):
    client = build_client(allowlist="ceos.wbs.get_tree")
    initialize(client, token)

    listed = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        headers=mcp_headers(token),
    )
    assert "ceos.wbs.get_tree" in listed.text
    assert "ceos.contract.list" not in listed.text

    refused = call_tool(client, token, "ceos.contract.list", {})
    assert refused["result"]["isError"] is True
    assert "許可されていない" in refused["result"]["content"][0]["text"]
