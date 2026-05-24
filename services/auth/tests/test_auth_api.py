"""認証API 結合テスト（ルート検証、入力バリデーション、認証ガード）"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db


class MockResult:
    def scalar_one_or_none(self):
        return None

    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None


@pytest.fixture
def app():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockResult()

    mock_db.execute = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_missing_fields(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 422


def test_login_empty_body(client):
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


def test_refresh_invalid_token(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-refresh-token-string"},
    )
    assert response.status_code == 401


def test_refresh_missing_token(client):
    response = client.post("/api/v1/auth/refresh", json={})
    assert response.status_code == 422


def test_mfa_verify_invalid_session(client):
    response = client.post(
        "/api/v1/auth/mfa/verify",
        json={"session_token": "invalid-session", "code": "123456"},
    )
    assert response.status_code == 400


def test_mfa_verify_missing_fields(client):
    response = client.post("/api/v1/auth/mfa/verify", json={})
    assert response.status_code == 422


def test_auth_required_for_mfa_setup(client):
    response = client.post("/api/v1/auth/mfa/setup", json={})
    assert response.status_code == 401


def test_auth_required_for_users(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_auth_required_for_roles(client):
    response = client.get(
        "/api/v1/roles?organization_id=00000000-0000-0000-0000-000000000001"
    )
    assert response.status_code == 401


def test_auth_required_for_clients(client):
    response = client.get(
        "/api/v1/api-clients?organization_id=00000000-0000-0000-0000-000000000001"
    )
    assert response.status_code == 401


def test_unknown_route_returns_404(client):
    response = client.get("/api/v1/nonexistent-route")
    assert response.status_code == 404
