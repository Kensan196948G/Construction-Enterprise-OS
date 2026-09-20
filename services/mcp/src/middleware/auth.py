"""認証ミドルウェア — Auth Service 発行の JWT を検証する

services/construction と同じ JWT/OIDC パターンを踏襲する。
MCP の読み取りツールは有効なユーザートークンを必須とする。
"""

from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError as JWTError

from ..config import get_settings

security = HTTPBearer(auto_error=False)


@dataclass
class TokenData:
    sub: str
    type: str
    org: str | None = None
    roles: list[str] | None = None
    scopes: list[str] | None = None


def decode_token(token: str) -> TokenData | None:
    """JWT を検証してペイロードを返す。無効・期限切れの場合は None。"""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_public_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        return TokenData(
            sub=payload["sub"],
            type=payload.get("type", "user"),
            org=payload.get("org"),
            roles=payload.get("roles", []),
            scopes=payload.get("scopes", []),
        )
    except (JWTError, KeyError):
        return None


def extract_bearer_token(authorization: str | None) -> str | None:
    """Authorization ヘッダーから Bearer トークンを取り出す。"""
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def authenticate_bearer(authorization: str | None) -> TokenData | None:
    """Authorization ヘッダーを検証し、ユーザートークンなら TokenData を返す。"""
    token = extract_bearer_token(authorization)
    if token is None:
        return None
    data = decode_token(token)
    if data is None or data.type != "user":
        return None
    return data


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData:
    """FastAPI 依存関係としてのユーザー認証（未認証は 401/403）。"""
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
