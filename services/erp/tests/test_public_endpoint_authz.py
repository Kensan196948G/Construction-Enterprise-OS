"""未認証でアクセスできないことの回帰テスト。

固定データを返すだけのエンドポイントが認証なしで公開されていると、
実データへ差し替えた時点で無認証の情報漏洩になる。
"""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client():
    # pytest-django の `client` に取られないようローカルに定義する
    return TestClient(create_app())


def test_erp_materials_requires_authentication(client):
    response = client.get("/api/v1/erp/materials")
    assert response.status_code in (401, 403)


def test_erp_ledger_summary_requires_authentication(client):
    response = client.get("/api/v1/erp/ledger/summary")
    assert response.status_code in (401, 403)
