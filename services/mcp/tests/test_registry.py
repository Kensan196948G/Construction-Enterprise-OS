"""ツールレジストリのテスト（ネットワーク非依存）

- 公開ツールは読み取り専用の 5 件のみ
- definition_sha256 は決定的で、定義変更時に必ず変化する
- ハッシュ欠落・不一致・禁止種別ではロードを拒否する
"""

from dataclasses import replace

import pytest

from src.tools import (
    FORBIDDEN_EFFECTS,
    REGISTRY,
    ToolRegistry,
    compute_definition_sha256,
    load_registry,
)
from src.tools.definitions import TOOL_DEFINITIONS
from src.tools.registry import RegistryIntegrityError

EXPECTED_TOOL_NAMES = {
    "ceos.wbs.get_tree",
    "ceos.schedule.get_gantt",
    "ceos.cost.list",
    "ceos.ledger.get_summary",
    "ceos.contract.list",
}


@pytest.fixture(autouse=True)
def _loaded_registry():
    load_registry()


def test_registry_contains_exactly_five_read_only_tools():
    assert REGISTRY.names == EXPECTED_TOOL_NAMES
    assert len(REGISTRY.definitions) == 5


def test_every_tool_is_read_only_r0_get():
    for definition in REGISTRY.definitions:
        assert definition.effect == "read"
        assert definition.tier == "R0"
        assert definition.upstream_method == "GET"
        assert definition.input_schema["type"] == "object"


def test_no_write_approve_or_external_send_effect_exists():
    effects = {str(definition.effect) for definition in REGISTRY.definitions}
    assert effects == {"read"}
    assert effects.isdisjoint(FORBIDDEN_EFFECTS)
    # 禁止 effect を名乗る定義はレジストリがロードを拒否する
    for forbidden in sorted(FORBIDDEN_EFFECTS):
        broken = replace(TOOL_DEFINITIONS[0], effect=forbidden, definition_sha256="")
        with pytest.raises(RegistryIntegrityError):
            ToolRegistry([broken]).load()


def test_each_definition_hash_is_pinned_and_reproducible():
    for definition in REGISTRY.definitions:
        assert len(definition.definition_sha256) == 64
        first = compute_definition_sha256(definition)
        second = compute_definition_sha256(definition)
        assert first == second == definition.definition_sha256


def test_hash_changes_when_any_field_changes():
    base = TOOL_DEFINITIONS[0]
    base_hash = compute_definition_sha256(base)

    mutations = {
        "name": replace(base, name=base.name + ".v2"),
        "description": replace(base, description=base.description + "（改訂）"),
        "input_schema": replace(
            base,
            input_schema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "extra": {"type": "string"},
                },
                "required": ["project_id"],
                "additionalProperties": False,
            },
        ),
        "effect": replace(base, effect="write"),
        "tier": replace(base, tier="R1"),
        "upstream_path": replace(base, upstream_path=base.upstream_path + "-v2"),
        "upstream_service": replace(base, upstream_service="security"),
        "upstream_method": replace(base, upstream_method="POST"),
    }

    for field, mutated in mutations.items():
        assert compute_definition_sha256(mutated) != base_hash, field


def test_registry_refuses_missing_hash():
    broken = replace(TOOL_DEFINITIONS[0], definition_sha256="")
    with pytest.raises(RegistryIntegrityError):
        ToolRegistry([broken]).load()


def test_registry_refuses_mismatched_hash():
    broken = replace(TOOL_DEFINITIONS[0], definition_sha256="0" * 64)
    with pytest.raises(RegistryIntegrityError):
        ToolRegistry([broken]).load()


def test_registry_refuses_non_get_method():
    broken = replace(
        TOOL_DEFINITIONS[0],
        upstream_method="POST",
        definition_sha256=compute_definition_sha256(
            replace(TOOL_DEFINITIONS[0], upstream_method="POST")
        ),
    )
    with pytest.raises(RegistryIntegrityError):
        ToolRegistry([broken]).load()


def test_registry_refuses_duplicate_names():
    with pytest.raises(RegistryIntegrityError):
        ToolRegistry([TOOL_DEFINITIONS[0], TOOL_DEFINITIONS[0]]).load()


def test_registry_access_before_load_is_refused():
    registry = ToolRegistry(TOOL_DEFINITIONS)
    with pytest.raises(Exception):
        _ = registry.names


def test_unknown_tool_is_not_found():
    assert REGISTRY.get("ceos.unknown.tool") is None
    with pytest.raises(Exception):
        REGISTRY.require("ceos.unknown.tool")


def test_required_parameters_match_upstream_contract():
    required = {
        definition.name: set(definition.input_schema.get("required", []))
        for definition in REGISTRY.definitions
    }
    assert required["ceos.wbs.get_tree"] == {"project_id"}
    assert required["ceos.schedule.get_gantt"] == {"project_id"}
    # 原価一覧は上流が工事台帳 ID を必須とする
    assert required["ceos.cost.list"] == {"ledger_id"}
    assert required["ceos.ledger.get_summary"] == set()
    assert required["ceos.contract.list"] == set()
