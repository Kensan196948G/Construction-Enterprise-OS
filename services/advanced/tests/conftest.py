from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db
from src.middleware.auth import get_current_user


async def _mock_get_current_user():
    return _make_mock_user()


def _make_mock_user(sub="00000000-0000-0000-0000-000000000001"):
    user = MagicMock()
    user.sub = sub
    user.type = "user"
    user.org = "00000000-0000-0000-0000-000000000001"
    user.roles = ["admin"]
    user.scopes = []
    return user


class MockResult:
    def __init__(self, return_value=None):
        self._return_value = return_value

    def scalar_one_or_none(self):
        return self._return_value

    def scalars(self):
        return self

    def all(self):
        if isinstance(self._return_value, list):
            return self._return_value
        return [self._return_value] if self._return_value else []

    def scalar(self):
        return self._return_value


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
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    _app.dependency_overrides[get_current_user] = _mock_get_current_user
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock-user-token"}


@pytest.fixture
def unauth_client():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockResult()

    mock_db.execute = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    return TestClient(_app)
