"""MFA 有効化・バックアップコードの挙動テスト"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pyotp
from fastapi.testclient import TestClient

from src.main import create_app
from src.middleware.auth_middleware import get_current_user
from src.models.base import get_db
from src.schemas import TokenData
from src.services.auth_service import hash_backup_code

SECRET = "JBSWY3DPEHPK3PXP"


class FakeUser:
    def __init__(self, **overrides):
        self.id = overrides.get("id", uuid.uuid4())
        self.email = overrides.get("email", "user@example.com")
        self.organization_id = overrides.get("organization_id", uuid.uuid4())
        self.status = overrides.get("status", "active")
        self.hashed_password = overrides.get("hashed_password", "unused")
        self.mfa_secret = overrides.get("mfa_secret")
        self.mfa_enabled = overrides.get("mfa_enabled", False)
        self.mfa_backup_codes = overrides.get("mfa_backup_codes")


class _Result:
    def __init__(self, user):
        self._user = user

    def scalar_one_or_none(self):
        return self._user

    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None


def _client(user):
    app = create_app()
    db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return _Result(user)

    db.execute = mock_execute
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()

    async def mock_get_db():
        yield db

    async def mock_get_current_user():
        return TokenData(sub=str(user.id), type="user", roles=["admin"])

    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    return TestClient(app), db


def test_mfa_activate_requires_auth():
    app = create_app()
    db = AsyncMock()

    async def mock_get_db():
        yield db

    app.dependency_overrides[get_db] = mock_get_db
    client = TestClient(app)
    res = client.post("/api/v1/auth/mfa/activate", json={"code": "123456"})
    assert res.status_code == 401


def test_mfa_activate_enables_mfa():
    user = FakeUser(mfa_secret=SECRET, mfa_enabled=False)
    client, _ = _client(user)

    code = pyotp.TOTP(SECRET).now()
    res = client.post("/api/v1/auth/mfa/activate", json={"code": code})

    assert res.status_code == 200
    assert res.json()["data"]["message"] == "MFAを有効化しました。"
    assert user.mfa_enabled is True


def test_mfa_activate_rejects_invalid_code():
    user = FakeUser(mfa_secret=SECRET, mfa_enabled=False)
    client, _ = _client(user)

    res = client.post("/api/v1/auth/mfa/activate", json={"code": "000000"})

    assert res.status_code == 400
    assert res.json()["detail"]["code"] == "INVALID_MFA_CODE"
    assert user.mfa_enabled is False


def test_mfa_activate_requires_prior_setup():
    user = FakeUser(mfa_secret=None, mfa_enabled=False)
    client, _ = _client(user)

    res = client.post("/api/v1/auth/mfa/activate", json={"code": "123456"})

    assert res.status_code == 400
    assert res.json()["detail"]["code"] == "MFA_NOT_SETUP"


def test_mfa_setup_rejected_when_already_enabled():
    user = FakeUser(mfa_secret=SECRET, mfa_enabled=True)
    client, _ = _client(user)

    res = client.post("/api/v1/auth/mfa/setup")

    assert res.status_code == 400
    assert res.json()["detail"]["code"] == "MFA_ALREADY_ENABLED"


def test_mfa_setup_persists_hashed_backup_codes():
    user = FakeUser(mfa_secret=None, mfa_enabled=False)
    client, _ = _client(user)

    res = client.post("/api/v1/auth/mfa/setup")

    assert res.status_code == 200
    plain_codes = res.json()["data"]["backup_codes"]
    assert len(plain_codes) == 10
    assert user.mfa_backup_codes is not None
    assert len(user.mfa_backup_codes) == 10
    assert all(code not in user.mfa_backup_codes for code in plain_codes)
    assert user.mfa_backup_codes == [hash_backup_code(c) for c in plain_codes]
