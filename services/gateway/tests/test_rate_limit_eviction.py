"""レート制限ミドルウェアのメモリ管理テスト。

追跡キーを削除しない実装だと、X-Forwarded-For を変え続けるだけで
キーが無限に増えメモリを枯渇させられる。
"""

from src.middleware.rate_limit import _MAX_TRACKED_CLIENTS, RateLimitMiddleware


def _middleware() -> RateLimitMiddleware:
    return RateLimitMiddleware(app=None)


def test_stale_client_is_evicted():
    middleware = _middleware()
    middleware._requests["1.1.1.1"] = [0.0]  # 60秒より前にしかアクセスが無い

    middleware._evict_stale_clients(now=1000.0)

    assert "1.1.1.1" not in middleware._requests


def test_recent_client_is_kept():
    middleware = _middleware()
    middleware._requests["2.2.2.2"] = [999.0]

    middleware._evict_stale_clients(now=1000.0)

    assert "2.2.2.2" in middleware._requests


def test_tracked_clients_are_capped():
    middleware = _middleware()
    for index in range(_MAX_TRACKED_CLIENTS + 50):
        middleware._requests[f"10.0.{index // 256}.{index % 256}"] = [999.0 + index]

    middleware._evict_stale_clients(now=999.0 + _MAX_TRACKED_CLIENTS + 50)

    assert len(middleware._requests) <= _MAX_TRACKED_CLIENTS


def test_oldest_clients_are_dropped_first():
    middleware = _middleware()
    middleware._requests["old"] = [999.0]
    for index in range(_MAX_TRACKED_CLIENTS):
        middleware._requests[f"new-{index}"] = [1000.0]

    middleware._evict_stale_clients(now=1000.0)

    assert "old" not in middleware._requests
    assert len(middleware._requests) == _MAX_TRACKED_CLIENTS
