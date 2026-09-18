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
