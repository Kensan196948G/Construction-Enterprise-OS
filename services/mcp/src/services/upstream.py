"""上流 CEOS サービスへの HTTP クライアント

MCP サービスは読み取りのみを行う。呼び出し元の Authorization ヘッダーを
そのまま転送し、上流側の認可（組織・案件・ロール）に委ねる。
"""

from dataclasses import dataclass
from typing import Any

import httpx

from ..config import Settings, get_settings


@dataclass
class UpstreamResult:
    """上流サービスの応答。"""

    status_code: int
    data: Any
    ok: bool


class UpstreamUnavailableError(RuntimeError):
    """上流サービスへ到達できない（接続失敗・タイムアウト）。"""


class UpstreamClient:
    """httpx ベースの読み取り専用クライアント。"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._settings.UPSTREAM_TIMEOUT_SECONDS
            )
        return self._client

    async def get(
        self,
        service: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        authorization: str | None = None,
    ) -> UpstreamResult:
        """上流サービスの GET を実行する。"""
        base_url = self._settings.upstream_base_url(service)
        url = f"{base_url}{path}"
        headers: dict[str, str] = {}
        if authorization:
            headers["Authorization"] = authorization

        client = await self._get_client()
        try:
            response = await client.get(url, params=params or {}, headers=headers)
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            raise UpstreamUnavailableError(
                f"上流サービスに到達できません: {service}"
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamUnavailableError(
                f"上流サービス呼び出しに失敗しました: {service}"
            ) from exc

        data: Any
        try:
            data = response.json()
        except ValueError:
            data = response.text

        return UpstreamResult(
            status_code=response.status_code,
            data=data,
            ok=200 <= response.status_code < 300,
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


_client: UpstreamClient | None = None


def get_upstream_client() -> UpstreamClient:
    """プロセス共有の上流クライアントを返す（遅延生成）。"""
    global _client
    if _client is None:
        _client = UpstreamClient(get_settings())
    return _client


def set_upstream_client(client: UpstreamClient | None) -> None:
    """テスト等で上流クライアントを差し替える。"""
    global _client
    _client = client


async def close_upstream_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
