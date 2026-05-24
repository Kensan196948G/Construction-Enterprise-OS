"""HTTPプロキシサービス"""

import httpx
import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class ProxyService:
    """上流マイクロサービスへのリクエスト転送を担当"""

    def __init__(self, timeout: float = 30.0):
        self._timeout = timeout

    async def forward(
        self,
        request: Request,
        upstream_url: str,
        upstream_name: str | None = None,
    ) -> Response:
        """リクエストを上流サービスに転送してレスポンスを返す"""
        path = request.url.path
        if request.url.query:
            path = f"{path}?{request.url.query}"

        target_url = f"{upstream_url.rstrip('/')}{path}"

        headers = self._prepare_headers(request)

        body = await request.body() if request.method in ("POST", "PUT", "PATCH", "DELETE") else None

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                upstream_response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    follow_redirects=False,
                )

                response_headers = dict(upstream_response.headers)

                # Remove hop-by-hop headers
                for hop_header in ("transfer-encoding", "connection", "keep-alive"):
                    response_headers.pop(hop_header, None)

                if upstream_name:
                    response_headers["X-Upstream-Service"] = upstream_name

                return Response(
                    content=upstream_response.content,
                    status_code=upstream_response.status_code,
                    headers=response_headers,
                )

        except httpx.TimeoutException:
            logger.error("upstream timeout", target_url=target_url)
            return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": {
                        "code": "GATEWAY_TIMEOUT",
                        "message": "上流サービスがタイムアウトしました。",
                    },
                },
            )
        except httpx.ConnectError:
            logger.error("upstream unavailable", target_url=target_url)
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "error": {
                        "code": "BAD_GATEWAY",
                        "message": "上流サービスに接続できません。",
                    },
                },
            )
        except Exception as exc:
            logger.exception("proxy error", target_url=target_url, error=str(exc))
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "error": {
                        "code": "BAD_GATEWAY",
                        "message": "上流サービスでエラーが発生しました。",
                    },
                },
            )

    @staticmethod
    def _prepare_headers(request: Request) -> dict[str, str]:
        """転送用ヘッダーを準備（hop-by-hop ヘッダーを除外）"""
        excluded = {"host", "transfer-encoding", "connection", "keep-alive"}
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in excluded
        }

        # Forward the original request ID if present
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            headers["X-Request-ID"] = request_id

        return headers
