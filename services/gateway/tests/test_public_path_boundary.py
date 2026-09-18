"""公開パスの境界の回帰テスト。

_is_public_path は re.match で判定するため、末尾を区切らないパターンは
前方一致で別のパスまで公開してしまう("^/api/v1/health" が
"/api/v1/healthcheck" にも一致する)。
"""

from src.middleware.auth import AuthMiddleware


def _middleware() -> AuthMiddleware:
    return AuthMiddleware(app=None)


def test_health_aggregate_is_public():
    assert _middleware()._is_public_path("/api/v1/health/services") is True


def test_path_sharing_the_prefix_is_not_public():
    assert _middleware()._is_public_path("/api/v1/healthcheck") is False


def test_unrelated_api_path_is_not_public():
    assert _middleware()._is_public_path("/api/v1/users") is False
