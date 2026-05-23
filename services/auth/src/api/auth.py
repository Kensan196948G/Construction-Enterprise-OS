"""認証エンドポイント（ログイン/ログアウト/リフレッシュ/MFA）"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db
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
    revoke_refresh_token,
    save_refresh_token,
    verify_mfa_code,
    verify_password,
)
from ..services.token_service import create_access_token

router = APIRouter()


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """ログイン"""
    user = await get_user_by_email(db, body.email)

    # ユーザー存在確認（存在しなくても同じエラーを返す = 列挙対策）
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
            detail={"code": "INVALID_CREDENTIALS", "message": "メールアドレスまたはパスワードが正しくありません。"},
        )

    # アカウント状態チェック
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "アカウントが無効です。管理者に連絡してください。"},
        )

    # ロックアウトチェック
    can_attempt, lock_msg = await check_login_attempts(user)
    if not can_attempt:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "ACCOUNT_LOCKED", "message": lock_msg},
        )

    # パスワード検証
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
            detail={"code": "INVALID_CREDENTIALS", "message": "メールアドレスまたはパスワードが正しくありません。"},
        )

    # MFAが有効な場合
    if user.mfa_enabled:
        session_token = secrets.token_urlsafe(32)
        # TODO: MFAセッショントークンをRedisに保存
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

    # トークン発行
    access_token = create_access_token(
        subject=str(user.id),
        org=str(user.organization_id),
        roles=[],  # TODO: DBからロール取得
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
    """トークンリフレッシュ"""
    token_hash = hash_token(body.refresh_token)
    # TODO: DBからリフレッシュトークンを検証、新しいトークンを発行
    # 古いトークンは revoke

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_REFRESH_TOKEN", "message": "リフレッシュトークンが無効です。"},
    )


@router.post("/logout")
async def logout(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """ログアウト（リフレッシュトークン無効化）"""
    token_hash = hash_token(body.refresh_token)
    await revoke_refresh_token(db, token_hash)

    return APIResponse(data={"message": "ログアウトしました。"})


@router.post("/mfa/setup", response_model=APIResponse[MFASetupResponse])
async def mfa_setup(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """MFA設定開始"""
    # TODO: 認証済みユーザーから取得
    email = "temp@example.com"
    secret = generate_mfa_secret()
    qr_url = generate_mfa_qr_url(email, secret)
    backup_codes = generate_backup_codes()

    # TODO: secret とバックアップコードのハッシュをDBに保存

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
    # TODO: RedisからMFAセッションを取得、コード検証、トークン発行
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": "INVALID_MFA_CODE", "message": "認証コードが無効です。"},
    )


@router.post("/mfa/disable")
async def mfa_disable(
    request: Request,
    body: MFADisableRequest,
    db: AsyncSession = Depends(get_db),
):
    """MFA無効化"""
    # TODO: パスワード検証後、MFAを無効化
    return APIResponse(data={"message": "MFAを無効化しました。"})
