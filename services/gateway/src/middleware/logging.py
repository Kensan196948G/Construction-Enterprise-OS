"""リクエスト/レスポンスロギングミドルウェア"""

import time
import uuid
from typing import Any

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """リクエスト/レスポンスをログ出力し、X-Request-ID を付与する"""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.monotonic()

        response = await call_next(request)

        duration_ms = (time.monotonic() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=self._get_client_ip(request),
            request_id=request_id,
        )

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
