"""認証サービス ユニットテスト（パスワード、MFA、ログイン試行制限）"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from src.services.auth_service import (
    check_login_attempts,
    hash_password,
    record_failed_login,
    record_successful_login,
    verify_mfa_code,
    verify_password,
)


class FakeUser:
    login_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None


def test_hash_password():
    pw = "test-password-12345"
    hashed = hash_password(pw)
    assert hashed != pw
    assert hashed.startswith("$2b$")


def test_verify_password_success():
    pw = "my-secure-password-123"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


def test_verify_password_wrong():
    pw = "correct-password-123"
    hashed = hash_password(pw)
    assert verify_password("wrong-password", hashed) is False


@pytest.mark.asyncio
async def test_check_login_attempts_not_locked():
    user = FakeUser()
    user.locked_until = None
    can_attempt, msg = await check_login_attempts(user)
    assert can_attempt is True
    assert msg is None


@pytest.mark.asyncio
async def test_check_login_attempts_locked():
    user = FakeUser()
    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
    can_attempt, msg = await check_login_attempts(user)
    assert can_attempt is False
    assert "ロック" in msg


@pytest.mark.asyncio
async def test_check_login_attempts_lock_expired():
    user = FakeUser()
    user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
    can_attempt, msg = await check_login_attempts(user)
    assert can_attempt is True


@pytest.mark.asyncio
async def test_record_failed_login():
    user = FakeUser()
    user.login_attempts = 0
    user.locked_until = None
    mock_db = AsyncMock()
    await record_failed_login(mock_db, user)
    assert user.login_attempts == 1
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_record_failed_login_lockout():
    user = FakeUser()
    user.login_attempts = 4
    user.locked_until = None
    mock_db = AsyncMock()
    await record_failed_login(mock_db, user)
    assert user.login_attempts == 5
    assert user.locked_until is not None


@pytest.mark.asyncio
async def test_record_successful_login():
    user = FakeUser()
    user.login_attempts = 3
    user.locked_until = datetime.now(timezone.utc)
    mock_db = AsyncMock()
    await record_successful_login(mock_db, user)
    assert user.login_attempts == 0
    assert user.locked_until is None
    assert user.last_login_at is not None


def test_verify_mfa_code():
    secret = "JBSWY3DPEHPK3PXP"
    import pyotp
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()
    assert verify_mfa_code(secret, valid_code) is True
