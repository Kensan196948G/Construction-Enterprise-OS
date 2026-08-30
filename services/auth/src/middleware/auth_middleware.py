"""認証ミドルウェア"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.base import get_db
from ..schemas import TokenData
from ..services.permission_service import user_has_permission
from ..services.token_service import decode_token

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: AsyncSession = Depends(get_db),
) -> TokenData:
    """JWTトークンから現在のユーザー情報を取得"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_REQUIRED", "message": "認証が必要です。"},
        )

    token_data = decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "トークンが無効または期限切れです。",
            },
        )

    if token_data.type != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "このAPIにはユーザートークンが必要です。",
            },
        )

    return token_data


async def get_current_client(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData:
    """M2Mトークンからクライアント情報を取得"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_REQUIRED", "message": "認証が必要です。"},
        )

    token_data = decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "トークンが無効または期限切れです。",
            },
        )

    if token_data.type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "このAPIにはM2Mトークンが必要です。",
            },
        )

    return token_data


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: AsyncSession = Depends(get_db),
) -> TokenData | None:
    """Optional auth — returns None when no Bearer token is present."""
    if not credentials:
        return None
    return decode_token(credentials.credentials)


def require_permission(resource: str, action: str):
    """権限チェック依存性。DB上の Permission/RolePermission/UserRole を参照して検証する"""

    async def permission_check(
        token_data: TokenData = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> TokenData:
        required = f"{resource}:{action}"
        # 管理者は全権限を持つ
        if "admin" in token_data.roles:
            return token_data

        try:
            user_id = uuid.UUID(token_data.sub)
        except ValueError:
            user_id = None

        if user_id is None or not await user_has_permission(
            db, user_id, resource, action
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSION",
                    "message": f"この操作には '{required}' 権限が必要です。",
                },
            )

        return token_data

    return permission_check


def require_role(role_name: str):
    """ロールチェック依存性"""

    async def role_check(
        token_data: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if role_name not in token_data.roles and "admin" not in token_data.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_ROLE",
                    "message": f"この操作には '{role_name}' ロールが必要です。",
                },
            )
        return token_data

    return role_check
