"""レート制限ミドルウェア（インメモリ実装）"""

import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings

settings = get_settings()

# 追跡する IP の上限。X-Forwarded-For は偽装可能なため、上限が無いと
# ヘッダを変え続けるだけでキーが無限に増えメモリを枯渇させられる。
_MAX_TRACKED_CLIENTS = 10_000


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IPアドレス単位のインメモリレート制限"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - 60

        window = [t for t in self._requests.get(client_ip, ()) if t > window_start]

        if len(window) >= settings.RATE_LIMIT_PER_MINUTE:
            # 窓を残したまま 429 を返す（次の判定でも同じ窓を使う）
            self._requests[client_ip] = window
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

        self._requests[client_ip] = [*window, now]
        self._evict_stale_clients(now)
        return await call_next(request)

    def _evict_stale_clients(self, now: float) -> None:
        """窓が空になった IP を削除し、追跡数を上限内に保つ。"""
        window_start = now - 60
        stale = [
            ip
            for ip, stamps in self._requests.items()
            if not stamps or stamps[-1] <= window_start
        ]
        for ip in stale:
            self._requests.pop(ip, None)

        if len(self._requests) <= _MAX_TRACKED_CLIENTS:
            return

        # 直近のアクセスが古い順に落とす
        ordered = sorted(self._requests.items(), key=lambda item: item[1][-1])
        for ip, _ in ordered[: len(self._requests) - _MAX_TRACKED_CLIENTS]:
            self._requests.pop(ip, None)

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
