"""ツール定義の型と正規化ロジック

MCP ツールの定義は「読み取り専用・R0」に限定する。

ハッシュは 2 種類を固定保持する（いずれも RFC 8785 JCS で正規化した JSON の SHA-256）。

- ``definition_sha256``: Mirai-Harness-Core のツール定義ハッシュ規約
  （対象キー name/title/description/inputSchema/outputSchema/annotations/x-mirai）。
  Core の Allowlist（``registries/mcp-allowlist.yaml``）に登録する値と同一になる。
- ``binding_sha256``: CEOS 内部の上流バインディング（name と upstream の service/method/path）。
  Core 規約の対象外だが、上流の差し替えを検知するため CEOS 側で固定する。
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
    title: str
    description: str
    input_schema: dict[str, Any]
    effect: ToolEffect
    tier: ToolTier
    upstream_service: str
    upstream_method: str
    upstream_path: str
    definition_sha256: str = ""
    binding_sha256: str = ""

    def annotations(self) -> dict[str, bool]:
        """MCP 標準注釈。x-mirai.effect と矛盾しないよう effect から導出する。"""
        read_only = self.effect == "read"
        return {
            "readOnlyHint": read_only,
            "destructiveHint": not read_only,
            "idempotentHint": read_only,
            "openWorldHint": False,
        }

    def x_mirai(self) -> dict[str, str]:
        """Core 拡張注釈 ``x-mirai``。

        ``operation`` は Core 承認階層表（approval-tiers/tiers.yaml）に CEOS 読み取り用の
        カテゴリが未定義のため付与しない（推測値を入れない。ADR-0002 未決事項）。
        """
        return {"effect": self.effect, "tier": self.tier}

    def contract_payload(self) -> dict[str, Any]:
        """Core 形式のツール契約（contracts/mcp-tools/<server>.json の 1 要素）。"""
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": self.annotations(),
            "x-mirai": self.x_mirai(),
        }

    def binding_payload(self) -> dict[str, Any]:
        """上流バインディング（binding_sha256 の対象）。"""
        return {
            "name": self.name,
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
