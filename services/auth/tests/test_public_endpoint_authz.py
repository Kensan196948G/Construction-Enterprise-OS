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


def test_users_organizations_requires_authentication(client):
    response = client.get("/api/v1/users/organizations")
    assert response.status_code in (401, 403)


def test_auth_ad_groups_requires_authentication(client):
    response = client.get("/api/v1/auth/ad/groups")
    assert response.status_code in (401, 403)


def test_auth_entra_policies_requires_authentication(client):
    response = client.get("/api/v1/auth/entra/policies")
    assert response.status_code in (401, 403)


def test_api_clients_requires_authentication(client):
    response = client.get("/api/v1/api-clients")
    assert response.status_code in (401, 403)
