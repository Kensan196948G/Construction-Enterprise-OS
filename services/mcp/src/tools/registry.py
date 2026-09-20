"""ツールレジストリ — 定義の検証とハッシュ固定（hash-pinning）

- 読み取り専用（effect="read", tier="R0", HTTP GET）以外を拒否する。
- ``definition_sha256`` が欠落・不一致の定義があればロードを拒否する（fail-closed）。
"""

import hashlib
import json
from collections.abc import Iterable

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


def canonical_json(payload: dict) -> str:
    """決定的な正規化 JSON 文字列を返す。

    sort_keys / 最小セパレータ / ensure_ascii=False を固定し、
    同一の定義から常に同一のハッシュが得られるようにする。
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def compute_definition_sha256(definition: ToolDefinition) -> str:
    """定義本体の正規化 JSON に対する SHA-256（hex）を返す。"""
    canonical = canonical_json(definition.canonical_payload())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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

        if not definition.definition_sha256:
            raise RegistryIntegrityError(
                f"definition_sha256 が欠落しています: {definition.name}"
            )

        computed = compute_definition_sha256(definition)
        if computed != definition.definition_sha256:
            raise RegistryIntegrityError(
                "definition_sha256 が一致しません（定義が変更されています）: "
                f"{definition.name} expected={definition.definition_sha256} "
                f"computed={computed}"
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
