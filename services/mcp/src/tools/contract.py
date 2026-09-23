"""Core 形式のツール契約（contracts/mcp-tools/ceos.json）の生成

レジストリを唯一の正本とし、Mirai-Harness-Core の ``contracts/mcp-tools/<server>.json`` と
同じ形式の文書を生成する。生成物はリポジトリ直下 ``contracts/mcp-tools/ceos.json`` に置き、
CI（tests/test_contract_export.py）でレジストリとのドリフトを検査する。

再生成: ``python -m src.tools.contract --write ../../contracts/mcp-tools/ceos.json``
"""

import argparse
import json
from pathlib import Path
from typing import Any

from .registry import ToolRegistry

# Core registries/systems.yaml の ceos.mcp_server_id と一致させる（適合テストで検査）。
SERVER_ID = "ceos"


def contract_document(registry: ToolRegistry) -> dict[str, Any]:
    """Core 形式のツール契約文書を返す（ツール名順）。"""
    return {
        "server_id": SERVER_ID,
        "tools": [
            definition.contract_payload()
            for definition in sorted(registry.definitions, key=lambda d: d.name)
        ],
    }


def render_contract(registry: ToolRegistry) -> str:
    """契約文書を決定的な整形 JSON 文字列にする（末尾改行付き）。"""
    return json.dumps(contract_document(registry), ensure_ascii=False, indent=2) + "\n"


def main() -> None:  # pragma: no cover - 手動再生成用 CLI
    from . import load_registry

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="出力先（未指定なら標準出力）")
    args = parser.parse_args()
    text = render_contract(load_registry())
    if args.write:
        args.write.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":  # pragma: no cover
    main()
