"""認証ビジネスロジック"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import pyotp
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import AuditLog, RefreshToken, User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_token_id() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def verify_mfa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret, interval=settings.MFA_TOKEN_VALIDITY_SECONDS)
    return totp.verify(code)


def generate_mfa_qr_url(email: str, secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.MFA_ISSUER)


def generate_backup_codes(count: int = 10) -> list[str]:
    return [secrets.token_hex(4) for _ in range(count)]


async def create_audit_log(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    event_type: str,
    event_data: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    success: bool = True,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        event_type=event_type,
        event_data=event_data or {},
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
    )
    db.add(log)
    return log


async def save_refresh_token(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    token: str,
    device_info: dict | None = None,
    ip_address: str | None = None,
    expires_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS,
) -> RefreshToken:
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

    rt = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        device_info=device_info or {},
        ip_address=ip_address,
        expires_at=expires_at,
    )
    db.add(rt)
    return rt


async def revoke_refresh_token(db: AsyncSession, token_hash: str) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token = result.scalar_one_or_none()
    if token:
        token.revoked_at = datetime.now(timezone.utc)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def check_login_attempts(user: User) -> tuple[bool, str | None]:
    """
    ログイン試行回数チェック
    Returns: (can_attempt, error_message)
    """
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() // 60)
        return False, f"アカウントがロックされています。あと{remaining}分お待ちください。"
    return True, None


async def record_failed_login(db: AsyncSession, user: User) -> None:
    user.login_attempts += 1
    if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=settings.LOGIN_LOCKOUT_MINUTES
        )


async def record_successful_login(db: AsyncSession, user: User) -> None:
    user.login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
