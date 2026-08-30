"""権限一覧API 結合テスト"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.middleware.auth_middleware import get_current_user
from src.models.base import get_db
from src.schemas import TokenData

USER_ID = "11111111-1111-1111-1111-111111111111"


class MockResult:
    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []


@pytest.fixture
def mock_db():
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockResult()

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


def test_list_permissions_as_admin(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["admin"]))
    response = client.get("/api/v1/permissions")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["permissions"] == []
    assert body["data"]["total"] == 0
    assert body["meta"]["page"] == 1


def test_list_permissions_without_permission_role_is_denied(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["field"]))
    response = client.get("/api/v1/permissions")
    assert response.status_code == 403


def test_list_permissions_requires_auth():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/permissions")
    assert response.status_code == 401
