"""認証エンドポイント（ログイン/ログアウト/リフレッシュ/MFA）"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db_retry import is_transient_db_error, rollback_safely
from ..models import RefreshToken, User, UserRole, Role
from ..models.base import async_session, get_db
from ..schemas import (
    APIResponse,
    ErrorDetail,
    LoginRequest,
    LoginResponse,
    MFADisableRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    RefreshRequest,
    RefreshResponse,
)
from ..services.auth_service import (
    check_login_attempts,
    create_audit_log,
    generate_backup_codes,
    generate_mfa_qr_url,
    generate_mfa_secret,
    generate_token_id,
    get_user_by_email,
    hash_token,
    record_failed_login,
    record_successful_login,
    save_refresh_token,
    verify_mfa_code,
    verify_password,
)
from ..services.token_service import create_access_token
from ..middleware.auth_middleware import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


def _create_mfa_session_token(user_id: str, email: str) -> str:
    """MFA検証用の短命セッショントークン（JWT方式）"""
    import jwt
    from ..config import get_settings

    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "purpose": "mfa_verify",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    return jwt.encode(
        payload, settings.jwt_private_key, algorithm=settings.JWT_ALGORITHM
    )


def _decode_mfa_session_token(token: str) -> dict | None:
    """MFAセッショントークン検証"""
    import jwt
    from jwt import InvalidTokenError as JWTError
    from ..config import get_settings

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_public_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        if payload.get("purpose") != "mfa_verify":
            return None
        return payload
    except JWTError:
        return None


async def _get_user_roles(db: AsyncSession, user: User) -> list[str]:
    """ユーザーのロール名一覧を取得"""
    result = await db.execute(
        select(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )
    return list(result.scalars().all())


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """ログイン(R6対策: 過渡的DBエラー時は新しいセッションで自動リトライ)"""
    try:
        return await _perform_login(request, body, db)
    except Exception as exc:
        if not is_transient_db_error(exc):
            raise
        logger.warning(
            "auth.login: 過渡的DBエラーを検知、新しいセッションで再試行します: %s",
            exc,
        )
        await rollback_safely(db)
        async with async_session() as retry_db:
            try:
                result = await _perform_login(request, body, retry_db)
                await retry_db.commit()
                return result
            except Exception:
                await retry_db.rollback()
                raise


async def _perform_login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession,
):
    """ログインの実処理(セッションのコミットは呼び出し元が担う)"""
    user = await get_user_by_email(db, body.email)

    if not user:
        await create_audit_log(
            db,
            user_id=None,
            event_type="auth.login.failed",
            event_data={"email": body.email, "reason": "user_not_found"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "メールアドレスまたはパスワードが正しくありません。",
            },
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_DISABLED",
                "message": "アカウントが無効です。管理者に連絡してください。",
            },
        )

    can_attempt, lock_msg = await check_login_attempts(user)
    if not can_attempt:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "ACCOUNT_LOCKED", "message": lock_msg},
        )

    if not verify_password(body.password, user.hashed_password):
        await record_failed_login(db, user)
        await create_audit_log(
            db,
            user_id=user.id,
            event_type="auth.login.failed",
            event_data={"reason": "wrong_password"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "メールアドレスまたはパスワードが正しくありません。",
            },
        )

    if user.mfa_enabled:
        session_token = _create_mfa_session_token(str(user.id), user.email)
        return APIResponse(
            data=LoginResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                expires_in=0,
                requires_mfa=True,
                mfa_session_token=session_token,
            )
        )

    roles = await _get_user_roles(db, user)
    access_token = create_access_token(
        subject=str(user.id),
        org=str(user.organization_id),
        roles=roles,
        device_id=body.device_name,
    )
    refresh_token_str = generate_token_id()
    await save_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token_str,
        device_info={"device_name": body.device_name},
        ip_address=request.client.host if request.client else None,
    )

    await record_successful_login(db, user)
    await create_audit_log(
        db,
        user_id=user.id,
        event_type="auth.login.success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return APIResponse(
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=3600,
        )
    )


@router.post("/refresh", response_model=APIResponse[RefreshResponse])
async def refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """トークンリフレッシュ(R6対策: 過渡的DBエラー時は新しいセッションで自動リトライ)"""
    try:
        return await _perform_refresh(request, body, db)
    except Exception as exc:
        if not is_transient_db_error(exc):
            raise
        logger.warning(
            "auth.refresh: 過渡的DBエラーを検知、新しいセッションで再試行します: %s",
            exc,
        )
        await rollback_safely(db)
        async with async_session() as retry_db:
            try:
                result = await _perform_refresh(request, body, retry_db)
                await retry_db.commit()
                return result
            except Exception:
                await retry_db.rollback()
                raise


async def _perform_refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession,
):
    """トークンリフレッシュの実処理(セッションのコミットは呼び出し元が担う)"""
    token_hash = hash_token(body.refresh_token)

    result = await db.execute(
        select(RefreshToken)
        .options(selectinload(RefreshToken.user).selectinload(User.roles))
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "リフレッシュトークンが無効です。",
            },
        )

    if stored_token.expires_at < datetime.now(timezone.utc):
        stored_token.revoked_at = datetime.now(timezone.utc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "EXPIRED_REFRESH_TOKEN",
                "message": "リフレッシュトークンの有効期限が切れています。",
            },
        )

    user = stored_token.user
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "アカウントが無効です。"},
        )

    stored_token.revoked_at = datetime.now(timezone.utc)

    roles = await _get_user_roles(db, user)
    access_token = create_access_token(
        subject=str(user.id),
        org=str(user.organization_id),
        roles=roles,
    )
    new_refresh_token_str = generate_token_id()
    await save_refresh_token(
        db,
        user_id=user.id,
        token=new_refresh_token_str,
        ip_address=request.client.host if request.client else None,
    )

    await create_audit_log(
        db,
        user_id=user.id,
        event_type="auth.token.refresh",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return APIResponse(
        data=RefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token_str,
            token_type="bearer",
            expires_in=3600,
        )
    )


@router.post("/logout")
async def logout(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """ログアウト（リフレッシュトークン無効化）"""
    token_hash = hash_token(body.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token:
        stored_token.revoked_at = datetime.now(timezone.utc)

    return APIResponse(data={"message": "ログアウトしました。"})


@router.post("/logout-all")
async def logout_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """全セッションログアウト（全リフレッシュトークン無効化）"""
    from uuid import UUID

    user_id = UUID(current_user.sub)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    tokens = result.scalars().all()
    for t in tokens:
        t.revoked_at = datetime.now(timezone.utc)

    await create_audit_log(
        db,
        user_id=user_id,
        event_type="auth.logout.all",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return APIResponse(data={"message": "全セッションからログアウトしました。"})


@router.post("/mfa/setup", response_model=APIResponse[MFASetupResponse])
async def mfa_setup(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """MFA設定開始"""
    from uuid import UUID

    user_id = UUID(current_user.sub)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません。"},
        )

    secret = generate_mfa_secret()
    qr_url = generate_mfa_qr_url(user.email, secret)
    backup_codes = generate_backup_codes()

    user.mfa_secret = secret

    return APIResponse(
        data=MFASetupResponse(
            secret=secret,
            qr_code_url=qr_url,
            backup_codes=backup_codes,
        )
    )


@router.post("/mfa/verify")
async def mfa_verify(
    request: Request,
    body: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """MFAコード検証"""
    payload = _decode_mfa_session_token(body.session_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SESSION",
                "message": "MFAセッションが無効または期限切れです。再度ログインしてください。",
            },
        )

    from uuid import UUID

    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "アカウントが無効です。"},
        )

    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MFA_NOT_SETUP", "message": "MFAが設定されていません。"},
        )

    if not verify_mfa_code(user.mfa_secret, body.code):
        return APIResponse(
            error=ErrorDetail(
                code="INVALID_MFA_CODE", message="認証コードが無効です。"
            ),
            success=False,
        )

    roles = await _get_user_roles(db, user)
    access_token = create_access_token(
        subject=str(user.id),
        org=str(user.organization_id),
        roles=roles,
    )
    refresh_token_str = generate_token_id()
    await save_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token_str,
        ip_address=request.client.host if request.client else None,
    )

    await record_successful_login(db, user)
    await create_audit_log(
        db,
        user_id=user.id,
        event_type="auth.mfa.success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return APIResponse(
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=3600,
        )
    )


@router.post("/mfa/disable")
async def mfa_disable(
    request: Request,
    body: MFADisableRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """MFA無効化"""
    from uuid import UUID

    user_id = UUID(current_user.sub)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "ユーザーが見つかりません。"},
        )

    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "WRONG_PASSWORD",
                "message": "パスワードが正しくありません。",
            },
        )

    if user.mfa_secret and not verify_mfa_code(user.mfa_secret, body.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_MFA_CODE", "message": "認証コードが無効です。"},
        )

    user.mfa_enabled = False
    user.mfa_secret = None

    await create_audit_log(
        db,
        user_id=user.id,
        event_type="auth.mfa.disabled",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return APIResponse(data={"message": "MFAを無効化しました。"})
