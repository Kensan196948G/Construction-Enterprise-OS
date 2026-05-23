"""テスト共通設定"""

import pytest


def pytest_configure(config):
    """pytest設定 - Flask pluginとの競合を回避"""
    # pytest-flask が FastAPI を Flask と誤認するのを防ぐ
    for plugin in ["pytest_flask"]:
        try:
            config.pluginmanager.set_blocked(plugin)
        except Exception:
            pass

    # asyncio マーカーを登録
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
