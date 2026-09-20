"""認証のテスト（ネットワーク非依存）

MCP の読み取りツールは有効なユーザートークンを必須とする。
"""

from tests.helpers import initialize, make_token, mcp_headers


def test_tools_call_without_token_is_refused(build_client):
    client = build_client()
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "ceos.wbs.get_tree", "arguments": {}},
        },
        headers=mcp_headers(None),
    )
    assert response.status_code in (401, 403)


def test_tools_list_without_token_is_refused(build_client):
    client = build_client()
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers=mcp_headers(None),
    )
    assert response.status_code in (401, 403)


def test_invalid_signature_token_is_refused(build_client):
    client = build_client()
    bad_token = make_token(key="wrong-signing-key-0123456789abcdef")
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers=mcp_headers(bad_token),
    )
    assert response.status_code in (401, 403)


def test_expired_token_is_refused(build_client):
    client = build_client()
    expired = make_token(expires_in=-60)
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers=mcp_headers(expired),
    )
    assert response.status_code in (401, 403)


def test_non_user_token_is_forbidden(build_client):
    client = build_client()
    service_token = make_token(sub="svc-1", token_type="service")
    response = client.post(
        "/mcp/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers=mcp_headers(service_token),
    )
    assert response.status_code == 403


def test_valid_token_is_accepted(build_client, token):
    client = build_client()
    result = initialize(client, token)
    assert "result" in result
    assert result["result"]["serverInfo"]["name"] == "ceos-mcp"


def test_health_is_unauthenticated(build_client):
    client = build_client()
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "ceos-mcp"
    assert len(payload["registered_tools"]) == 5


def test_tools_call_requires_token_even_for_unknown_tool(build_client):
    client = build_client()
    response = client.post(
        "/mcp/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "ceos.unknown.tool", "arguments": {}},
        },
        headers=mcp_headers(None),
    )
    # 認証層で拒否されるため JSON-RPC には到達しない
    assert response.status_code in (401, 403)
