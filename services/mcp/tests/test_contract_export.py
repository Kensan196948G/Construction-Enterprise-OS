"""Core 形式ツール契約（contracts/mcp-tools/ceos.json）のドリフト検査

リポジトリに置いた契約ファイルがレジストリ（唯一の正本）から生成したものと
完全一致することを確認する。不一致時の再生成手順は src/tools/contract.py を参照。
"""

import json
from pathlib import Path

from src.tools import load_registry
from src.tools.contract import SERVER_ID, contract_document, render_contract
from src.tools.registry import tool_contract_sha256

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPO_ROOT / "contracts" / "mcp-tools" / "ceos.json"


def test_committed_contract_matches_registry():
    committed = CONTRACT_PATH.read_text(encoding="utf-8")
    assert committed == render_contract(load_registry()), (
        "contracts/mcp-tools/ceos.json がレジストリと一致しません。"
        "services/mcp で `python -m src.tools.contract --write "
        "../../contracts/mcp-tools/ceos.json` を実行して再生成してください。"
    )


def test_contract_hashes_match_pinned_definition_hashes():
    registry = load_registry()
    document = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert document["server_id"] == SERVER_ID
    pinned = {d.name: d.definition_sha256 for d in registry.definitions}
    computed = {tool["name"]: tool_contract_sha256(tool) for tool in document["tools"]}
    assert computed == pinned


def test_contract_excludes_internal_upstream_binding():
    """上流 URL/パスは CEOS 内部の実装詳細であり、共有契約へ出さない。"""
    document = contract_document(load_registry())
    for tool in document["tools"]:
        assert "upstream" not in tool
        assert set(tool) <= {
            "name",
            "title",
            "description",
            "inputSchema",
            "outputSchema",
            "annotations",
            "x-mirai",
        }
