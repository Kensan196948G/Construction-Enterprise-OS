"""JWT検証ミドルウェア"""

import re
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """JWTトークンを検証し、リクエスト状態にユーザー情報を注入する"""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        path = request.url.path

        if self._is_public_path(path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "AUTH_REQUIRED",
                        "message": "認証が必要です。",
                    },
                },
            )

        token = auth_header[7:]
        token_data = self._decode_token(token)
        if token_data is None:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "トークンが無効または期限切れです。",
                    },
                },
            )

        request.state.user = {
            "sub": token_data.get("sub"),
            "type": token_data.get("type"),
            "org": token_data.get("org"),
            "roles": token_data.get("roles", []),
            "scopes": token_data.get("scopes", []),
        }

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        if not self._matches_any_upstream(path):
            return True
        for pattern in settings.PUBLIC_PATHS:
            if re.match(pattern, path):
                return True
        return False

    @staticmethod
    def _matches_any_upstream(path: str) -> bool:
        for pattern in settings.UPSTREAM_SERVICES:
            if re.match(pattern, path):
                return True
        return False

    def _decode_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            return payload
        except JWTError:
            return None
