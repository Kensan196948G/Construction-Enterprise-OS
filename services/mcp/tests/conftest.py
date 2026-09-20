"""テスト共通設定

``src.config`` を読み込む前に環境変数を確定させる（JWT 鍵・キルスイッチ）。
"""

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_PUBLIC_KEY", "test-only-mcp-key-0123456789abcdef")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("MCP_ENABLED", "1")
os.environ.setdefault("MCP_TOOL_ALLOWLIST", "")

from collections.abc import Iterator  # noqa: E402
from typing import Any, Callable  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.services import upstream  # noqa: E402
from tests.helpers import FakeUpstreamClient, make_token  # noqa: E402


def pytest_configure(config: Any) -> None:
    for plugin in ["pytest_flask"]:
        try:
            config.pluginmanager.set_blocked(plugin)
        except Exception:
            pass


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _reset_upstream_client() -> Iterator[None]:
    """各テスト後に上流クライアントの差し替えを戻す。"""
    yield
    upstream.set_upstream_client(None)


@pytest.fixture
def build_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., TestClient]]:
    """環境変数を切り替えて MCP アプリを構築するファクトリ。"""
    from src.main import create_app

    created: list[TestClient] = []

    def _build(enabled: bool = True, allowlist: str = "") -> TestClient:
        monkeypatch.setenv("MCP_ENABLED", "1" if enabled else "0")
        monkeypatch.setenv("MCP_TOOL_ALLOWLIST", allowlist)
        get_settings.cache_clear()
        client = TestClient(create_app())
        client.__enter__()
        created.append(client)
        return client

    yield _build

    for client in created:
        client.__exit__(None, None, None)
    get_settings.cache_clear()


@pytest.fixture
def token() -> str:
    """有効なユーザートークン。"""
    return make_token()


@pytest.fixture
def fake_upstream() -> Iterator[FakeUpstreamClient]:
    """上流サービスを差し替えるフェイク（ネットワーク非依存）。"""
    fake = FakeUpstreamClient()
    upstream.set_upstream_client(fake)
    yield fake
    upstream.set_upstream_client(None)
