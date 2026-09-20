"""MCP エンドポイント用 ASGI ガード

MCP の Streamable HTTP サブアプリは独自にリクエストを処理するため、
FastAPI の依存関係ではなく ASGI ミドルウェアとして次を強制する（fail-closed）。

1. キルスイッチ: MCP_ENABLED が無効なら 503 で全リクエストを拒否する。
2. 認証: 有効なユーザー JWT（Bearer）が無ければ 401、ユーザートークン以外は 403。

ツール単位の許可リストは ``src.tools.policy`` が ``tools/call`` 時に強制する。
"""

from typing import Any

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ..config import get_settings
from .auth import decode_token, extract_bearer_token


async def _send_json(
    scope: Scope,
    receive: Receive,
    send: Send,
    status_code: int,
    body: dict[str, Any],
) -> None:
    response = JSONResponse(status_code=status_code, content=body)
    await response(scope, receive, send)


class McpGuardMiddleware:
    """MCP サブアプリを包み、キルスイッチと認証を強制する ASGI ミドルウェア。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        settings = get_settings()

        if not settings.mcp_enabled:
            await _send_json(
                scope,
                receive,
                send,
                503,
                {
                    "success": False,
                    "error": {
                        "code": "MCP_DISABLED",
                        "message": "MCP サーバーは無効化されています。",
                    },
                },
            )
            return

        authorization = Headers(scope=scope).get("authorization")
        token = extract_bearer_token(authorization)
        if token is None:
            await _send_json(
                scope,
                receive,
                send,
                401,
                {
                    "success": False,
                    "error": {
                        "code": "AUTH_REQUIRED",
                        "message": "認証が必要です。",
                    },
                },
            )
            return

        token_data = decode_token(token)
        if token_data is None:
            await _send_json(
                scope,
                receive,
                send,
                401,
                {
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "トークンが無効または期限切れです。",
                    },
                },
            )
            return

        if token_data.type != "user":
            await _send_json(
                scope,
                receive,
                send,
                403,
                {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "このAPIにはユーザートークンが必要です。",
                    },
                },
            )
            return

        await self.app(scope, receive, send)
