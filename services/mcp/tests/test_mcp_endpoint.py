"""MCP エンドポイント（Streamable HTTP）のテスト

上流はフェイクに差し替えるためネットワークへは出ない。
"""

import json
import logging

from src.services.upstream import UpstreamResult
from src.tools import RESULT_OK, load_registry
from src.tools.contract import contract_document
from tests.helpers import (
    call_tool,
    initialize,
    list_tools,
)

EXPECTED_TOOL_NAMES = {
    "ceos.wbs.get_tree",
    "ceos.schedule.get_gantt",
    "ceos.cost.list",
    "ceos.ledger.get_summary",
    "ceos.contract.list",
}


def test_initialize_reports_server_info(build_client, token):
    client = build_client()
    result = initialize(client, token)
    assert result["result"]["serverInfo"]["name"] == "ceos-mcp"
    assert "tools" in result["result"]["capabilities"]


def test_tools_list_returns_exactly_the_five_read_only_tools(build_client, token):
    client = build_client()
    initialize(client, token)
    result = list_tools(client, token)
    tools = result["result"]["tools"]
    assert {tool["name"] for tool in tools} == EXPECTED_TOOL_NAMES
    assert len(tools) == 5
    for tool in tools:
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["destructiveHint"] is False
        assert tool["inputSchema"]["type"] == "object"


def test_tools_list_matches_core_contract_fields(build_client, token):
    """tools/list の公開値が Core 形式の契約（ハッシュ対象）と一致する。"""
    client = build_client()
    initialize(client, token)
    listed = {t["name"]: t for t in list_tools(client, token)["result"]["tools"]}
    for contract_tool in contract_document(load_registry())["tools"]:
        live = listed[contract_tool["name"]]
        for key in ("title", "description", "inputSchema", "annotations"):
            assert live[key] == contract_tool[key], (contract_tool["name"], key)


def test_tools_call_unknown_tool_is_refused(build_client, token, fake_upstream):
    client = build_client()
    initialize(client, token)
    result = call_tool(client, token, "ceos.unknown.tool", {})
    assert result["result"]["isError"] is True
    assert fake_upstream.calls == []


def test_tools_call_success_returns_upstream_payload(
    build_client, token, fake_upstream
):
    fake_upstream.response = UpstreamResult(
        status_code=200, data={"items": [{"id": "wbs-1"}]}, ok=True
    )
    client = build_client()
    initialize(client, token)
    result = call_tool(
        client,
        token,
        "ceos.wbs.get_tree",
        {"project_id": "11111111-1111-1111-1111-111111111111"},
    )
    assert result["result"]["isError"] is False
    payload = json.loads(result["result"]["content"][0]["text"])
    assert payload == {"items": [{"id": "wbs-1"}]}
    assert fake_upstream.calls[0]["path"] == "/api/v1/construction/wbs/tree"
    assert fake_upstream.calls[0]["authorization"].startswith("Bearer ")


def test_tools_call_upstream_error_is_reported(build_client, token, fake_upstream):
    fake_upstream.response = UpstreamResult(status_code=500, data={}, ok=False)
    client = build_client()
    initialize(client, token)
    result = call_tool(client, token, "ceos.ledger.get_summary", {})
    assert result["result"]["isError"] is True


def test_tools_call_writes_audit_log_without_business_data(
    build_client, token, fake_upstream, caplog
):
    marker = "S3CRET_BUSINESS_DETAIL"
    fake_upstream.response = UpstreamResult(
        status_code=200, data={"items": [{"note": marker}]}, ok=True
    )
    client = build_client()
    initialize(client, token)

    with caplog.at_level(logging.INFO, logger="ceos_mcp.audit"):
        call_tool(
            client,
            token,
            "ceos.ledger.get_summary",
            {},
        )

    records = [record.getMessage() for record in caplog.records]
    audit_lines = [line for line in records if "mcp_tools_call" in line]
    assert len(audit_lines) == 1
    line = audit_lines[0]
    assert "caller=user-1" in line
    assert "tool=ceos.ledger.get_summary" in line
    assert f"result={RESULT_OK}" in line
    assert "latency_ms=" in line
    # 業務データ（応答本文）は info で記録しない
    assert marker not in line


def test_tools_call_refusal_is_audited(build_client, token, fake_upstream, caplog):
    client = build_client()
    initialize(client, token)
    with caplog.at_level(logging.INFO, logger="ceos_mcp.audit"):
        call_tool(client, token, "ceos.unknown.tool", {})
    line = [
        record.getMessage()
        for record in caplog.records
        if "mcp_tools_call" in record.getMessage()
    ][0]
    assert "result=TOOL_NOT_FOUND" in line
