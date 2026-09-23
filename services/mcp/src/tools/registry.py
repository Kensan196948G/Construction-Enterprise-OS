"""ツールレジストリ — 定義の検証とハッシュ固定（hash-pinning）

- 読み取り専用（effect="read", tier="R0", HTTP GET）以外を拒否する。
- ``definition_sha256``（Core 規約）/ ``binding_sha256``（上流バインディング）が
  欠落・不一致の定義があればロードを拒否する（fail-closed）。
- MCP 標準注釈（readOnlyHint）が x-mirai.effect と矛盾する定義を拒否する。
"""

import hashlib
from collections.abc import Iterable
from typing import Any

import rfc8785

from .models import (
    ALLOWED_EFFECTS,
    ALLOWED_TIERS,
    FORBIDDEN_EFFECTS,
    ToolDefinition,
)


class ToolRegistryError(RuntimeError):
    """ツールレジストリ関連の基底例外。"""


class RegistryIntegrityError(ToolRegistryError):
    """定義の欠落・ハッシュ不一致・禁止種別など、レジストリの完全性違反。"""


class ToolNotFoundError(ToolRegistryError):
    """未登録のツールが要求された。"""


# Mirai-Harness-Core のツール定義ハッシュ規約（tools/tool_def_hash.py）の対象キー。
# 実行時の値（_meta 等）は含めない。
CORE_HASHED_KEYS: tuple[str, ...] = (
    "name",
    "title",
    "description",
    "inputSchema",
    "outputSchema",
    "annotations",
    "x-mirai",
)


def canonical_json(payload: dict[str, Any]) -> bytes:
    """RFC 8785（JCS）で正規化した JSON バイト列を返す。"""
    return rfc8785.dumps(payload)


def tool_contract_sha256(tool: dict[str, Any]) -> str:
    """Core 形式のツール契約 1 件に対する定義ハッシュ（Core 規約と同一）。"""
    subset = {key: tool[key] for key in CORE_HASHED_KEYS if key in tool}
    return hashlib.sha256(canonical_json(subset)).hexdigest()


def compute_definition_sha256(definition: ToolDefinition) -> str:
    """ツール定義の Core 規約ハッシュ（Allowlist 登録値）を返す。"""
    return tool_contract_sha256(definition.contract_payload())


def compute_binding_sha256(definition: ToolDefinition) -> str:
    """上流バインディングのハッシュを返す。"""
    return hashlib.sha256(canonical_json(definition.binding_payload())).hexdigest()


class ToolRegistry:
    """MCP ツール定義のレジストリ。"""

    def __init__(self, definitions: Iterable[ToolDefinition]) -> None:
        self._definitions: tuple[ToolDefinition, ...] = tuple(definitions)
        self._by_name: dict[str, ToolDefinition] = {}
        self._loaded = False

    # --- ロードと検証 ---------------------------------------------------
    def load(self) -> "ToolRegistry":
        """全定義を検証する。違反があれば RegistryIntegrityError を送出する。"""
        by_name: dict[str, ToolDefinition] = {}
        for definition in self._definitions:
            self._verify_definition(definition)
            if definition.name in by_name:
                raise RegistryIntegrityError(
                    f"ツール名が重複しています: {definition.name}"
                )
            by_name[definition.name] = definition
        self._by_name = by_name
        self._loaded = True
        return self

    def _verify_definition(self, definition: ToolDefinition) -> None:
        if not definition.name:
            raise RegistryIntegrityError("ツール名が空です。")

        effect = str(definition.effect)
        if effect in FORBIDDEN_EFFECTS:
            raise RegistryIntegrityError(
                f"禁止された effect です（読み取り専用のみ許可）: "
                f"{definition.name} effect={effect}"
            )
        if effect not in ALLOWED_EFFECTS:
            raise RegistryIntegrityError(
                f"未許可の effect です: {definition.name} effect={effect}"
            )

        tier = str(definition.tier)
        if tier not in ALLOWED_TIERS:
            raise RegistryIntegrityError(
                f"未許可の tier です（R0 のみ許可）: {definition.name} tier={tier}"
            )

        if str(definition.upstream_method).upper() != "GET":
            raise RegistryIntegrityError(
                f"読み取り専用ツールは GET のみ許可されます: "
                f"{definition.name} method={definition.upstream_method}"
            )

        if not isinstance(definition.input_schema, dict) or (
            definition.input_schema.get("type") != "object"
        ):
            raise RegistryIntegrityError(
                f"input_schema は type=object の JSON Schema が必要です: {definition.name}"
            )

        if definition.annotations().get("readOnlyHint") is not (effect == "read"):
            raise RegistryIntegrityError(
                f"readOnlyHint が x-mirai.effect と矛盾しています: {definition.name}"
            )

        self._verify_hash(
            definition, "definition_sha256", compute_definition_sha256(definition)
        )
        self._verify_hash(
            definition, "binding_sha256", compute_binding_sha256(definition)
        )

    @staticmethod
    def _verify_hash(definition: ToolDefinition, field: str, computed: str) -> None:
        pinned = getattr(definition, field)
        if not pinned:
            raise RegistryIntegrityError(f"{field} が欠落しています: {definition.name}")
        if computed != pinned:
            raise RegistryIntegrityError(
                f"{field} が一致しません（定義が変更されています）: "
                f"{definition.name} expected={pinned} computed={computed}"
            )

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise ToolRegistryError(
                "レジストリがロードされていません。load() を先に呼び出してください。"
            )

    # --- 参照 -----------------------------------------------------------
    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def definitions(self) -> tuple[ToolDefinition, ...]:
        self._ensure_loaded()
        return self._definitions

    @property
    def names(self) -> frozenset[str]:
        self._ensure_loaded()
        return frozenset(self._by_name)

    def get(self, name: str) -> ToolDefinition | None:
        self._ensure_loaded()
        return self._by_name.get(name)

    def require(self, name: str) -> ToolDefinition:
        self._ensure_loaded()
        definition = self._by_name.get(name)
        if definition is None:
            raise ToolNotFoundError(f"未登録のツールです: {name}")
        return definition
