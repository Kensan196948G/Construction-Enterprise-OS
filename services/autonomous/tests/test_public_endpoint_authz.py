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


def test_autonomous_activities_requires_authentication(client):
    response = client.get("/api/v1/autonomous/activities")
    assert response.status_code in (401, 403)


def test_autonomous_drone_flights_requires_authentication(client):
    response = client.get("/api/v1/autonomous/drone-flights")
    assert response.status_code in (401, 403)


def test_autonomous_error_logs_requires_authentication(client):
    response = client.get("/api/v1/autonomous/error-logs")
    assert response.status_code in (401, 403)


def test_autonomous_machines_requires_authentication(client):
    response = client.get("/api/v1/autonomous/machines")
    assert response.status_code in (401, 403)


def test_autonomous_rpa_tasks_requires_authentication(client):
    response = client.get("/api/v1/autonomous/rpa-tasks")
    assert response.status_code in (401, 403)


def test_autonomous_twin_sensors_requires_authentication(client):
    response = client.get("/api/v1/autonomous/twin-sensors")
    assert response.status_code in (401, 403)
