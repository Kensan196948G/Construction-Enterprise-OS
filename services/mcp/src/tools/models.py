"""ツール定義の型と正規化ロジック

MCP ツールの定義は「読み取り専用・R0」に限定する。
``definition_sha256`` は定義本体（name/description/inputSchema/effect/tier/upstream）を
正規化 JSON にしたものの SHA-256 であり、定義改ざん・差し替えを検知するために固定保持する。
"""

from dataclasses import dataclass, field
from typing import Any, Literal

# 読み取り専用のみ許可する。write/propose/external_send 等は型・検証の両面で拒否する。
ToolEffect = Literal["read"]
# R0（参照のみ。承認・確定を伴わない）
ToolTier = Literal["R0"]

# 許可される effect / tier の集合（レジストリ検証で使用）
ALLOWED_EFFECTS: frozenset[str] = frozenset({"read"})
ALLOWED_TIERS: frozenset[str] = frozenset({"R0"})

# 明示的に禁止する effect（回帰検知用）
FORBIDDEN_EFFECTS: frozenset[str] = frozenset(
    {"write", "propose", "approve", "finalize", "delete", "pay", "external_send"}
)


@dataclass(frozen=True)
class ToolDefinition:
    """読み取り専用 MCP ツールの定義。"""

    name: str
    description: str
    input_schema: dict[str, Any]
    effect: ToolEffect
    tier: ToolTier
    upstream_service: str
    upstream_method: str
    upstream_path: str
    definition_sha256: str = ""

    def canonical_payload(self) -> dict[str, Any]:
        """ハッシュ計算の対象となる正規化前のペイロード。"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "effect": self.effect,
            "tier": self.tier,
            "upstream": {
                "service": self.upstream_service,
                "method": self.upstream_method,
                "path": self.upstream_path,
            },
        }


@dataclass
class ToolCallOutcome:
    """tools/call の実行結果（監査ログの result_code を含む）。"""

    result_code: str
    payload: dict[str, Any] | None = None
    error_message: str | None = None
    http_status: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.result_code != "OK"
