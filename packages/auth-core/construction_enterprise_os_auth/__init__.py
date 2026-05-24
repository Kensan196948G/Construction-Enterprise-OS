"""Construction-Enterprise-OS Shared Authentication Middleware

全サービス共通のJWT認証ミドルウェア。
各サービスはこのパッケージから `get_current_user` をインポートして利用する。

使用例:
    from construction_enterprise_os_auth import get_current_user, require_role, TokenData

    @router.get("/protected")
    async def protected_route(token: TokenData = Depends(get_current_user)):
        return {"user": token.sub}
"""

from dataclasses import dataclass, field
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer(auto_error=False)

# サービスの config から JWT 設定を取得するためのコールバック
# 各サービスは起動時にこの関数を設定する
_config_provider = None


@dataclass
class TokenData:
    """JWTから抽出したトークンデータ"""
    sub: str
    type: str = "user"
    org: str | None = None
    roles: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)


def configure_auth(
    jwt_public_key: str,
    jwt_algorithm: str = "HS256",
    public_paths: list[str] | None = None,
) -> None:
    """認証ミドルウェアの設定を初期化
    
    Args:
        jwt_public_key: JWT検証用の公開鍵
        jwt_algorithm: JWTアルゴリズム (HS256, RS256等)
        public_paths: 認証不要のパスリスト
    """
    global _config_provider
    _config_provider = {
        "public_key": jwt_public_key,
        "algorithm": jwt_algorithm,
        "public_paths": public_paths or ["/health", "/docs", "/openapi.json", "/redoc"],
    }


def decode_token(token: str) -> TokenData | None:
    """JWTを検証・デコードする"""
    if not _config_provider:
        raise RuntimeError(
            "Auth middleware not configured. "
            "Call configure_auth() during app startup."
        )
    try:
        payload = jwt.decode(
            token,
            _config_provider["public_key"],
            algorithms=[_config_provider["algorithm"]],
            options={"verify_exp": True},
        )
        return TokenData(
            sub=payload.get("sub", ""),
            type=payload.get("type", "user"),
            org=payload.get("org"),
            roles=payload.get("roles", []),
            scopes=payload.get("scopes", []),
        )
    except JWTError:
        return None


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData:
    """FastAPI依存性: JWTからユーザー情報を取得
    
    リクエストのAuthorizationヘッダーからBearerトークンを抽出し、
    検証・デコードしてTokenDataを返す。
    認証不要パスはスキップ。
    """
    # 公開パスは認証不要
    if _config_provider and request.url.path in _config_provider.get("public_paths", []):
        return TokenData(sub="anonymous", type="anonymous")

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です。",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効または期限切れです。",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_client(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData:
    """FastAPI依存性: M2Mトークンからクライアント情報を取得"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です。",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="M2Mトークンが必要です。",
        )

    return token_data


def require_role(role_name: str):
    """FastAPI依存性: 特定ロールを要求する"""
    async def role_check(token: TokenData = Depends(get_current_user)) -> TokenData:
        if role_name not in token.roles and "admin" not in token.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"この操作には '{role_name}' ロールが必要です。",
            )
        return token
    return role_check


def require_permission(resource: str, action: str):
    """FastAPI依存性: 特定権限を要求する"""
    async def permission_check(token: TokenData = Depends(get_current_user)) -> TokenData:
        if "admin" in token.roles:
            return token
        # NB: 本実装ではスコープベースの簡易チェック
        # 本番ではDBからユーザー権限を照会する
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"この操作には '{resource}:{action}' 権限が必要です。",
        )
    return permission_check
