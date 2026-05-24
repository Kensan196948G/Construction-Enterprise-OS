"""Autonomous Service 結合テスト"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db
from src.middleware.auth import get_current_user, get_current_client


class MockResult:
    def __init__(self, return_value=None):
        self._return_value = return_value

    def scalar_one_or_none(self):
        return self._return_value

    def scalars(self):
        return self

    def all(self):
        if isinstance(self._return_value, list):
            return self._return_value
        return [self._return_value] if self._return_value else []

    def scalar(self):
        return self._return_value


def _make_mock_user(sub="00000000-0000-0000-0000-000000000001"):
    user = MagicMock()
    user.sub = sub
    user.type = "user"
    user.org = "00000000-0000-0000-0000-000000000001"
    user.roles = ["admin"]
    user.scopes = []
    return user


def _make_mock_agent(agent_id=None):
    from datetime import datetime, timezone
    a = MagicMock()
    a.id = agent_id or uuid4()
    a.organization_id = uuid4()
    a.name = "Mock Agent"
    a.agent_type = "scheduler"
    a.status = "idle"
    a.target_resource = None
    a.config = {}
    a.last_run_at = None
    a.run_count = 0
    a.error_count = 0
    a.is_enabled = True
    a.created_at = datetime.now(timezone.utc)
    return a


def _make_mock_twin(twin_id=None):
    from datetime import datetime, timezone

    class MockTwin:
        def __init__(self):
            self.id = twin_id or uuid4()
            self.organization_id = uuid4()
            self.project_id = None
            self.name = "Mock Twin"
            self.twin_type = "construction_site"
            self.status = "active"
            self.bim_model_id = None
            self.iot_device_ids = []
            self.last_sync_at = datetime.now(timezone.utc)
            self.sync_interval_seconds = 60
            self.data_sources = {}
            self.current_state = {}
            self.metadata = {}
            self.metadata_ = {}
            self.created_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
    return MockTwin()


def _make_mock_task(task_id=None):
    from datetime import datetime, timezone
    t = MagicMock()
    t.id = task_id or uuid4()
    t.organization_id = uuid4()
    t.agent_id = None
    t.digital_twin_id = None
    t.title = "Mock Task"
    t.task_type = "optimize_schedule"
    t.priority = "normal"
    t.status = "pending"
    t.input_data = None
    t.output_data = None
    t.error_message = None
    t.started_at = None
    t.completed_at = None
    t.duration_ms = None
    t.created_at = datetime.now(timezone.utc)
    return t


def _make_mock_simulation(sim_id=None):
    from datetime import datetime, timezone
    s = MagicMock()
    s.id = sim_id or uuid4()
    s.organization_id = uuid4()
    s.project_id = None
    s.digital_twin_id = None
    s.name = "Mock Simulation"
    s.simulation_type = "schedule"
    s.status = "draft"
    s.parameters = {}
    s.results = {}
    s.progress_percent = 0
    s.started_at = None
    s.completed_at = None
    s.created_by = None
    s.created_at = datetime.now(timezone.utc)
    return s


async def _mock_get_current_user():
    return _make_mock_user()


async def _mock_get_current_client():
    client = MagicMock()
    client.sub = "00000000-0000-0000-0000-000000000002"
    client.type = "client"
    client.org = "00000000-0000-0000-0000-000000000001"
    client.roles = []
    client.scopes = ["autonomous:agent"]
    return client


@pytest.fixture
def app():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockResult()

    async def mock_commit():
        pass

    async def mock_rollback():
        pass

    async def mock_close():
        pass

    async def mock_flush():
        pass

    mock_db.execute = mock_execute
    mock_db.commit = mock_commit
    mock_db.rollback = mock_rollback
    mock_db.close = mock_close
    mock_db.flush = mock_flush
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    _app.dependency_overrides[get_current_user] = _mock_get_current_user
    _app.dependency_overrides[get_current_client] = _mock_get_current_client
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock-user-token"}


# ============================================
# Test 1: Health Check
# ============================================
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "autonomous-service"


# ============================================
# Test 2: Auth Required - Agent endpoint
# ============================================
def test_agents_list_requires_auth():
    _app = create_app()
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MockResult())
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    c = TestClient(_app)
    response = c.get("/api/v1/autonomous/agents")
    assert response.status_code == 401


# ============================================
# Test 3: Agent CRUD - Create
# ============================================
def test_create_agent(client, auth_headers):
    mock_agent = _make_mock_agent()

    import src.api.agents as agents_module
    agents_module.create_agent = AsyncMock(return_value=mock_agent)

    response = client.post(
        "/api/v1/autonomous/agents",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Test Scheduler",
            "agent_type": "scheduler",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Agent"


# ============================================
# Test 4: Agent CRUD - Get
# ============================================
def test_get_agent(client, auth_headers):
    agent_id = uuid4()
    mock_agent = _make_mock_agent(agent_id=agent_id)

    import src.api.agents as agents_module
    agents_module.get_agent_by_id = AsyncMock(return_value=mock_agent)

    response = client.get(
        f"/api/v1/autonomous/agents/{agent_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 5: Agent CRUD - Update
# ============================================
def test_update_agent(client, auth_headers):
    agent_id = uuid4()
    mock_agent = _make_mock_agent(agent_id=agent_id)

    import src.api.agents as agents_module
    agents_module.update_agent = AsyncMock(return_value=mock_agent)

    response = client.put(
        f"/api/v1/autonomous/agents/{agent_id}",
        json={"name": "Updated Agent"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 6: Agent CRUD - Delete
# ============================================
def test_delete_agent(client, auth_headers):
    agent_id = uuid4()

    import src.api.agents as agents_module
    agents_module.delete_agent = AsyncMock(return_value=True)

    response = client.delete(
        f"/api/v1/autonomous/agents/{agent_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 7: Agent Start/Stop
# ============================================
def test_start_agent(client, auth_headers):
    agent_id = uuid4()
    mock_agent = _make_mock_agent(agent_id=agent_id)

    import src.api.agents as agents_module
    agents_module.start_agent = AsyncMock(return_value=mock_agent)

    response = client.post(
        f"/api/v1/autonomous/agents/{agent_id}/start",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 8: Digital Twin CRUD - Create
# ============================================
def test_create_twin(client, auth_headers):
    mock_twin = _make_mock_twin()

    import src.api.digital_twins as twin_module
    twin_module.create_twin = AsyncMock(return_value=mock_twin)

    response = client.post(
        "/api/v1/autonomous/digital-twins",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Test Construction Site",
            "twin_type": "construction_site",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Twin"


# ============================================
# Test 9: Digital Twin CRUD - Get
# ============================================
def test_get_twin(client, auth_headers):
    twin_id = uuid4()
    mock_twin = _make_mock_twin(twin_id=twin_id)

    import src.api.digital_twins as twin_module
    twin_module.get_twin_by_id = AsyncMock(return_value=mock_twin)

    response = client.get(
        f"/api/v1/autonomous/digital-twins/{twin_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 10: Digital Twin Sync State
# ============================================
def test_sync_twin(client, auth_headers):
    twin_id = uuid4()
    mock_twin = _make_mock_twin(twin_id=twin_id)

    import src.api.digital_twins as twin_module
    twin_module.sync_twin = AsyncMock(return_value=mock_twin)

    response = client.post(
        f"/api/v1/autonomous/digital-twins/{twin_id}/sync",
        json={"current_state": {"status": "active"}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 11: Task Creation
# ============================================
def test_create_task(client, auth_headers):
    mock_task = _make_mock_task()

    import src.api.tasks as tasks_module
    tasks_module.create_task = AsyncMock(return_value=mock_task)

    response = client.post(
        "/api/v1/autonomous/tasks",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "title": "Optimize Construction Schedule",
            "task_type": "optimize_schedule",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Mock Task"


# ============================================
# Test 12: Task Get Result
# ============================================
def test_get_task(client, auth_headers):
    task_id = uuid4()
    mock_task = _make_mock_task(task_id=task_id)

    import src.api.tasks as tasks_module
    tasks_module.get_task_by_id = AsyncMock(return_value=mock_task)

    response = client.get(
        f"/api/v1/autonomous/tasks/{task_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 13: Simulation Create
# ============================================
def test_create_simulation(client, auth_headers):
    mock_sim = _make_mock_simulation()

    import src.api.simulations as sim_module
    sim_module.create_simulation = AsyncMock(return_value=mock_sim)

    response = client.post(
        "/api/v1/autonomous/simulations",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Schedule Simulation",
            "simulation_type": "schedule",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Simulation"


# ============================================
# Test 14: Simulation Run
# ============================================
def test_run_simulation(client, auth_headers):
    sim_id = uuid4()
    mock_sim = _make_mock_simulation(sim_id=sim_id)

    import src.api.simulations as sim_module
    sim_module.run_simulation = AsyncMock(return_value=mock_sim)

    response = client.post(
        f"/api/v1/autonomous/simulations/{sim_id}/run",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 15: Agent List Pagination
# ============================================
def test_list_agents(client, auth_headers):
    mock_agent = _make_mock_agent()

    import src.api.agents as agents_module
    agents_module.get_agents_paginated = AsyncMock(return_value=([mock_agent], 1))

    response = client.get(
        "/api/v1/autonomous/agents?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1


# ============================================
# Test 16: Twin List
# ============================================
def test_list_twins(client, auth_headers):
    mock_twin = _make_mock_twin()

    import src.api.digital_twins as twin_module
    twin_module.get_twins_paginated = AsyncMock(return_value=([mock_twin], 1))

    response = client.get(
        "/api/v1/autonomous/digital-twins?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1


# ============================================
# Test 17: Simulation List
# ============================================
def test_list_simulations(client, auth_headers):
    mock_sim = _make_mock_simulation()

    import src.api.simulations as sim_module
    sim_module.get_simulations_paginated = AsyncMock(return_value=([mock_sim], 1))

    response = client.get(
        "/api/v1/autonomous/simulations?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1
