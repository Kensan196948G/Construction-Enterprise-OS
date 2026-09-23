"""API ドキュメント（Swagger / ReDoc / OpenAPI）の公開範囲の回帰テスト。"""

import pytest
from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import create_app


@pytest.fixture
def make_client(monkeypatch):
    def _make(environment: str) -> TestClient:
        monkeypatch.setenv("ENVIRONMENT", environment)
        get_settings.cache_clear()
        return TestClient(create_app())

    yield _make
    get_settings.cache_clear()


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_docs_hidden_outside_development(make_client, path):
    client = make_client("test")
    assert client.get(path).status_code == 404


@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_docs_available_in_development(make_client, path):
    client = make_client("development")
    assert client.get(path).status_code == 200
