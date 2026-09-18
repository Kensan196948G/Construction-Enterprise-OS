"""ユーザー詳細取得の認可テスト。

get_user が get_current_user だけに依存していると、認証さえ通れば
users:read を持たない利用者でも任意のユーザー情報を読めてしまう。
兄弟エンドポイントと同じ require_permission("users", "read") を要求する。
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.middleware.auth_middleware import get_current_user
from src.models.base import get_db
from src.schemas import TokenData

USER_ID = "11111111-1111-1111-1111-111111111111"
TARGET_ID = "22222222-2222-2222-2222-222222222222"


class _EmptyResult:
    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []

    def scalar_one_or_none(self):
        return None


@pytest.fixture
def mock_db():
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return _EmptyResult()

    db.execute = mock_execute
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    return db


def _client_as(mock_db, token_data: TokenData) -> TestClient:
    app = create_app()

    async def mock_get_db():
        yield mock_db

    async def mock_get_current_user():
        return token_data

    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    return TestClient(app)


def test_user_detail_denied_without_users_read_permission(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["field"]))
    response = client.get(f"/api/v1/users/{TARGET_ID}")
    assert response.status_code == 403


def test_user_detail_allows_admin(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["admin"]))
    response = client.get(f"/api/v1/users/{TARGET_ID}")
    # 権限は通る。対象が存在しないため 404(403 ではない)
    assert response.status_code == 404


def test_user_detail_requires_authentication(mock_db):
    app = create_app()

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    response = TestClient(app).get(f"/api/v1/users/{TARGET_ID}")
    assert response.status_code in (401, 403)
