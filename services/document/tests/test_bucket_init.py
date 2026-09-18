"""MinIO バケット初期化が ENVIRONMENT に依存せず実行されることの回帰テスト。

development 限定にすると docker compose (ENVIRONMENT=docker) で
バケットが作られず、文書アップロードが必ず失敗する。
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import create_app


def test_bucket_is_initialised_in_docker_environment(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "docker")
    called: list[bool] = []

    def _record() -> bool:
        called.append(True)
        return True

    with patch("src.main.initialize_bucket", side_effect=_record):
        app = create_app()
        with TestClient(app):
            pass
    get_settings.cache_clear()

    assert called == [True], "ENVIRONMENT=docker でもバケット初期化が呼ばれること"
