"""レート制限ミドルウェア（インメモリ実装）"""

import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IPアドレス単位のインメモリレート制限"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - 60

        window = [t for t in self._requests[client_ip] if t > window_start]
        self._requests[client_ip] = window

        if len(window) >= settings.RATE_LIMIT_PER_MINUTE:
            retry_after = int(window[0] + 60 - now) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "リクエスト制限を超えました。しばらく待ってから再試行してください。",
                    },
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
