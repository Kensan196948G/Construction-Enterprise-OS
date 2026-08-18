"""認証API 結合テスト（ルート検証、入力バリデーション、認証ガード）"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

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


# ---------------------------------------------------------------------------
# R6対策: 過渡的DBエラー時の自動リトライ
# ---------------------------------------------------------------------------


class _RetrySession:
    """リトライ用の新セッションを模倣するコンテキストマネージャ"""

    def __init__(self, db):
        self._db = db

    async def __aenter__(self):
        return self._db

    async def __aexit__(self, *exc_info):
        return False


def _make_transient_error() -> OperationalError:
    return OperationalError(
        "SELECT ...", None, RuntimeError("connection refused: server is not running")
    )


def test_login_retries_with_fresh_session_on_transient_db_error(app, monkeypatch):
    """1回目の DB アクセスが接続過渡エラーでも、新セッションでリトライし
    INTERNAL_ERROR ではなく正常なレスポンス(ここでは 401)を返す"""
    from src.api import auth as auth_api

    calls = {"n": 0}

    async def flaky_get_user_by_email(db, email):
        calls["n"] += 1
        if calls["n"] == 1:
            raise _make_transient_error()
        return None  # 2回目: ユーザー不在 → 401 INVALID_CREDENTIALS

    monkeypatch.setattr(auth_api, "get_user_by_email", flaky_get_user_by_email)

    retry_db = AsyncMock()
    # 新セッションも既存モックと同様に全 execute が空結果を返すようにする
    async def mock_execute(*args, **kwargs):
        return MockResult()

    retry_db.execute = mock_execute
    retry_db.add = AsyncMock()
    retry_db.rollback = AsyncMock()
    monkeypatch.setattr(auth_api, "async_session", lambda: _RetrySession(retry_db))

    # 500 レスポンス本体を検証するため、サーバー例外の再送出を無効化する
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 401  # INTERNAL_ERROR(500) にならないこと
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"
    assert calls["n"] == 2  # リトライが実行されたこと


def test_login_does_not_retry_on_non_transient_error(app, monkeypatch):
    """通常の例外(非過渡)はリトライせず 500 INTERNAL_ERROR として伝播する"""
    from src.api import auth as auth_api

    calls = {"n": 0}

    async def broken_get_user_by_email(db, email):
        calls["n"] += 1
        raise ValueError("unexpected business bug")

    monkeypatch.setattr(auth_api, "get_user_by_email", broken_get_user_by_email)

    # 500 レスポンス本体を検証するため、サーバー例外の再送出を無効化する
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert calls["n"] == 1  # リトライされないこと


def test_engine_uses_pool_pre_ping():
    """R6対策: プールの失効コネクションを払い出す前に ping で検出する"""
    from src.models.base import engine

    assert engine.pool._pre_ping is True  # type: ignore[attr-defined]
