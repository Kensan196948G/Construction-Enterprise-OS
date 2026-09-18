"""既定テンプレートのシードが ENVIRONMENT に依存せず実行されることの回帰テスト。

development 限定にすると docker compose (ENVIRONMENT=docker) で
テンプレートが未投入となり、通知送信が常に 422 TEMPLATE_NOT_FOUND になる。
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import create_app


def test_default_templates_seeded_in_docker_environment(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "docker")
    calls: list[bool] = []

    async def _record(db) -> None:
        calls.append(True)

    with patch("src.main.ensure_default_templates", side_effect=_record):
        app = create_app()
        with TestClient(app):
            pass
    get_settings.cache_clear()

    assert calls == [True], "ENVIRONMENT=docker でもシードが呼ばれること"


def test_startup_fails_when_templates_cannot_be_seeded(monkeypatch):
    """シードできないまま healthy を返し続けないこと (fail-fast)。"""
    import pytest

    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "docker")
    monkeypatch.setattr("src.main._TEMPLATE_SEED_RETRY_SECONDS", 0)

    async def _always_fail(db) -> None:
        raise RuntimeError("db unavailable")

    with patch("src.main.ensure_default_templates", side_effect=_always_fail):
        app = create_app()
        with pytest.raises(RuntimeError):
            with TestClient(app):
                pass
    get_settings.cache_clear()
