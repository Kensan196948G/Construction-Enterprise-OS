"""ツール実行エンジンのテスト（ネットワーク非依存）

引数検証・パス/クエリ分割・上流エラーの result_code 変換を確認する。
"""

import pytest

from src.config import Settings
from src.services.upstream import UpstreamResult, UpstreamUnavailableError
from src.tools import (
    REGISTRY,
    RESULT_ARGUMENT_INVALID,
    RESULT_OK,
    RESULT_UPSTREAM_ERROR,
    RESULT_UPSTREAM_UNAVAILABLE,
    ToolArgumentError,
    build_upstream_request,
    execute_tool,
    load_registry,
    validate_arguments,
)
from tests.helpers import FakeUpstreamClient

PROJECT_ID = "11111111-1111-1111-1111-111111111111"
LEDGER_ID = "22222222-2222-2222-2222-222222222222"


@pytest.fixture(autouse=True)
def _loaded_registry():
    load_registry()


def test_build_request_substitutes_path_and_splits_query():
    gantt = REGISTRY.require("ceos.schedule.get_gantt")
    path, query = build_upstream_request(gantt, {"project_id": PROJECT_ID})
    assert path == f"/api/v1/construction/projects/{PROJECT_ID}/gantt"
    assert query == {}

    wbs = REGISTRY.require("ceos.wbs.get_tree")
    path, query = build_upstream_request(wbs, {"project_id": PROJECT_ID})
    assert path == "/api/v1/construction/wbs/tree"
    assert query == {"project_id": PROJECT_ID}


def test_validate_arguments_rejects_missing_required():
    wbs = REGISTRY.require("ceos.wbs.get_tree")
    with pytest.raises(ToolArgumentError):
        validate_arguments(wbs, {})


def test_validate_arguments_rejects_unknown_and_wrong_type():
    summary = REGISTRY.require("ceos.ledger.get_summary")
    with pytest.raises(ToolArgumentError):
        validate_arguments(summary, {"unexpected": "x"})

    costs = REGISTRY.require("ceos.cost.list")
    with pytest.raises(ToolArgumentError):
        validate_arguments(costs, {"ledger_id": LEDGER_ID, "page": "abc"})
    with pytest.raises(ToolArgumentError):
        validate_arguments(costs, {"ledger_id": 123})


def test_validate_arguments_enforces_integer_bounds():
    invoices = REGISTRY.require("ceos.contract.list")
    assert validate_arguments(invoices, {"page": "2", "per_page": 50}) == {
        "page": 2,
        "per_page": 50,
    }
    with pytest.raises(ToolArgumentError):
        validate_arguments(invoices, {"per_page": 101})


async def test_execute_tool_invalid_arguments():
    outcome = await execute_tool(
        "ceos.wbs.get_tree",
        {},
        authorization="Bearer x",
        client=FakeUpstreamClient(),
        registry=REGISTRY,
        settings=Settings(),
    )
    assert outcome.result_code == RESULT_ARGUMENT_INVALID


async def test_execute_tool_forwards_authorization_and_returns_payload():
    fake = FakeUpstreamClient(
        response=UpstreamResult(status_code=200, data={"items": [{"id": 1}]}, ok=True)
    )
    outcome = await execute_tool(
        "ceos.contract.list",
        {"status": "paid"},
        authorization="Bearer caller-token",
        client=fake,
        registry=REGISTRY,
        settings=Settings(),
    )
    assert outcome.result_code == RESULT_OK
    assert outcome.payload == {"items": [{"id": 1}]}
    assert fake.calls[0]["authorization"] == "Bearer caller-token"
    assert fake.calls[0]["service"] == "erp"
    assert fake.calls[0]["path"] == "/api/v1/erp/invoices"
    assert fake.calls[0]["params"] == {"status": "paid"}


async def test_execute_tool_cost_list_uses_ledger_path_param():
    fake = FakeUpstreamClient()
    await execute_tool(
        "ceos.cost.list",
        {"ledger_id": LEDGER_ID, "page": 1},
        authorization="Bearer x",
        client=fake,
        registry=REGISTRY,
        settings=Settings(),
    )
    assert fake.calls[0]["path"] == f"/api/v1/erp/ledger/{LEDGER_ID}/costs"
    assert fake.calls[0]["params"] == {"page": 1}


async def test_execute_tool_maps_upstream_error_status():
    fake = FakeUpstreamClient(
        response=UpstreamResult(status_code=404, data={"detail": "not found"}, ok=False)
    )
    outcome = await execute_tool(
        "ceos.ledger.get_summary",
        {},
        authorization="Bearer x",
        client=fake,
        registry=REGISTRY,
        settings=Settings(),
    )
    assert outcome.result_code == RESULT_UPSTREAM_ERROR
    assert outcome.http_status == 404


async def test_execute_tool_maps_unavailable_upstream():
    fake = FakeUpstreamClient(error=UpstreamUnavailableError("down"))
    outcome = await execute_tool(
        "ceos.ledger.get_summary",
        {},
        authorization="Bearer x",
        client=fake,
        registry=REGISTRY,
        settings=Settings(),
    )
    assert outcome.result_code == RESULT_UPSTREAM_UNAVAILABLE


async def test_execute_tool_wraps_non_dict_payload():
    fake = FakeUpstreamClient(
        response=UpstreamResult(status_code=200, data=[1, 2, 3], ok=True)
    )
    outcome = await execute_tool(
        "ceos.ledger.get_summary",
        {},
        authorization="Bearer x",
        client=fake,
        registry=REGISTRY,
        settings=Settings(),
    )
    assert outcome.result_code == RESULT_OK
    assert outcome.payload == {"data": [1, 2, 3]}
