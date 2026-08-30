"""require_permission の権限チェック結合テスト"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.middleware.auth_middleware import get_current_user, require_permission
from src.models.base import get_db
from src.schemas import TokenData

USER_ID = "11111111-1111-1111-1111-111111111111"


class MockResult:
    def scalar(self):
        return 0


def _make_app():
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        current_user: TokenData = Depends(require_permission("widgets", "read")),
    ):
        return {"ok": True}

    return app


def _override_current_user(token_data: TokenData):
    async def _get_current_user():
        return token_data

    return _get_current_user


@pytest.fixture
def app():
    return _make_app()


@pytest.fixture
def mock_db():
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockResult()

    db.execute = mock_execute
    return db


def test_admin_bypasses_permission_check(app, mock_db):
    app.dependency_overrides[get_current_user] = _override_current_user(
        TokenData(sub=USER_ID, type="user", roles=["admin"])
    )

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    client = TestClient(app)

    response = client.get("/protected")
    assert response.status_code == 200


def test_non_admin_without_permission_is_denied(app, mock_db):
    app.dependency_overrides[get_current_user] = _override_current_user(
        TokenData(sub=USER_ID, type="user", roles=["field"])
    )

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    client = TestClient(app)

    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=False),
    ):
        response = client.get("/protected")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "INSUFFICIENT_PERMISSION"


def test_non_admin_with_permission_is_allowed(app, mock_db):
    app.dependency_overrides[get_current_user] = _override_current_user(
        TokenData(sub=USER_ID, type="user", roles=["field"])
    )

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    client = TestClient(app)

    with patch(
        "src.middleware.auth_middleware.user_has_permission",
        new=AsyncMock(return_value=True),
    ):
        response = client.get("/protected")

    assert response.status_code == 200


def test_malformed_subject_is_denied(app, mock_db):
    app.dependency_overrides[get_current_user] = _override_current_user(
        TokenData(sub="not-a-uuid", type="user", roles=["field"])
    )

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    client = TestClient(app)

    response = client.get("/protected")
    assert response.status_code == 403
