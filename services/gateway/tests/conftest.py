"""テスト共通設定"""

import pytest


def pytest_configure(config):
    """pytest設定 - Flask pluginとの競合を回避"""
    for plugin in ["pytest_flask"]:
        try:
            config.pluginmanager.set_blocked(plugin)
        except Exception:
            pass

    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
