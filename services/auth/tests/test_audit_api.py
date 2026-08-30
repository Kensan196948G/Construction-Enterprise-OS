"""監査ログ検索API 結合テスト"""

from unittest.mock import AsyncMock, patch

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


def test_list_audit_logs_as_admin_with_db_permission(mock_db):
    """audit:read はadminバイパス対象外のため、DB権限があって初めて許可される(seed済みadminは実際にaudit:readを保持)"""
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["admin"]))
    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=True),
    ):
        response = client.get("/api/v1/audit-logs")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["logs"] == []
    assert body["data"]["total"] == 0


def test_list_audit_logs_with_filters_as_admin(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["admin"]))
    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=True),
    ):
        response = client.get(
            "/api/v1/audit-logs",
            params={"event_type": "login", "success": "true", "page": 1, "per_page": 10},
        )
    assert response.status_code == 200


def test_list_audit_logs_admin_without_db_permission_is_denied(mock_db):
    """admin ロールであっても DB に audit:read が付与されていなければ拒否される"""
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["admin"]))
    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=False),
    ):
        response = client.get("/api/v1/audit-logs")
    assert response.status_code == 403


def test_list_audit_logs_without_permission_role_is_denied(mock_db):
    client = _client_as(mock_db, TokenData(sub=USER_ID, type="user", roles=["field"]))
    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=False),
    ):
        response = client.get("/api/v1/audit-logs")
    assert response.status_code == 403


def test_list_audit_logs_requires_auth():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/audit-logs")
    assert response.status_code == 401
