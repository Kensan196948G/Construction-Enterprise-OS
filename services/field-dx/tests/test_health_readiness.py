"""DB 到達不能時に /health が 503 を返すことの回帰テスト。

到達性を確認せず常に 200 を返す実装だと、コンテナの healthcheck が
DB 断を検知できず監視が機能しない。
"""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db


def test_health_returns_503_when_database_unavailable():
    app = create_app()
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=RuntimeError("database unavailable"))

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db
    try:
        response = TestClient(app).get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
