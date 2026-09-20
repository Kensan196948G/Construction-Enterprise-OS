"""キルスイッチとツール許可リスト（fail-closed）

- ``MCP_ENABLED`` が無効ならサーバー全体を拒否する。
- ``MCP_TOOL_ALLOWLIST`` が設定されている場合、列挙されたツール以外は拒否する。
- 未登録のツールは許可リストの内容にかかわらず常に拒否する。
"""

from typing import TypedDict

from ..config import Settings, get_settings
from .registry import ToolRegistry


class PolicyDescription(TypedDict):
    enabled: bool
    allowlist: list[str] | None
    registered_tools: list[str]


def is_server_enabled(settings: Settings | None = None) -> bool:
    """MCP サーバー全体が有効かを返す。"""
    return (settings or get_settings()).mcp_enabled


def effective_allowlist(settings: Settings | None = None) -> frozenset[str] | None:
    """有効な許可リストを返す。None は「登録済み全ツールを許可」を意味する。"""
    return (settings or get_settings()).tool_allowlist


def is_tool_allowed(
    name: str,
    registry: ToolRegistry,
    settings: Settings | None = None,
) -> bool:
    """ツールが実行を許可されているかを判定する（fail-closed）。"""
    if name not in registry.names:
        return False
    allowlist = effective_allowlist(settings)
    if allowlist is None:
        return True
    return name in allowlist


def describe_policy(
    registry: ToolRegistry,
    settings: Settings | None = None,
) -> PolicyDescription:
    """ヘルスチェック等で公開するポリシー概要（機密は含めない）。"""
    resolved = settings or get_settings()
    allowlist = effective_allowlist(resolved)
    return PolicyDescription(
        enabled=is_server_enabled(resolved),
        allowlist=sorted(allowlist) if allowlist is not None else None,
        registered_tools=sorted(registry.names),
    )
