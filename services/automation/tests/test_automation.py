"""Automation Service 結合テスト"""

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


def _make_mock_rule(rule_id=None):
    from datetime import datetime, timezone
    r = MagicMock()
    r.id = rule_id or uuid4()
    r.organization_id = uuid4()
    r.name = "Mock Rule"
    r.description = "Test automation rule"
    r.trigger_type = "schedule"
    r.condition = {"field": "status", "operator": "eq", "value": "pending"}
    r.action = {"type": "notify", "config": {"channel": "email"}}
    r.is_active = True
    r.created_by = None
    r.last_triggered = None
    r.created_at = datetime.now(timezone.utc)
    r.updated_at = datetime.now(timezone.utc)
    return r


def _make_mock_task(task_id=None):
    from datetime import datetime, timezone
    t = MagicMock()
    t.id = task_id or uuid4()
    t.organization_id = uuid4()
    t.name = "Mock Task"
    t.description = "Test scheduled task"
    t.cron_expression = "0 */6 * * *"
    t.action_type = "execute"
    t.action_config = {"script": "backup.sh"}
    t.is_active = True
    t.created_by = None
    t.last_run = None
    t.next_run = None
    t.last_status = None
    t.created_at = datetime.now(timezone.utc)
    t.updated_at = datetime.now(timezone.utc)
    return t


def _make_mock_task_run(run_id=None, task_id=None):
    from datetime import datetime, timezone
    r = MagicMock()
    r.id = run_id or uuid4()
    r.task_id = task_id or uuid4()
    r.organization_id = uuid4()
    r.status = "completed"
    r.output_data = {"message": "executed successfully"}
    r.error_message = None
    r.started_at = datetime.now(timezone.utc)
    r.completed_at = datetime.now(timezone.utc)
    r.duration_ms = 150
    r.created_at = datetime.now(timezone.utc)
    return r


def _make_mock_trigger(trigger_id=None):
    from datetime import datetime, timezone
    t = MagicMock()
    t.id = trigger_id or uuid4()
    t.organization_id = uuid4()
    t.name = "Mock Trigger"
    t.description = "Test event trigger"
    t.event_type = "iot.device.alert"
    t.filter_conditions = {"device_type": "crane"}
    t.action_config = {"type": "webhook", "url": "https://example.com/hook"}
    t.is_active = True
    t.created_by = None
    t.last_triggered = None
    t.created_at = datetime.now(timezone.utc)
    t.updated_at = datetime.now(timezone.utc)
    return t


async def _mock_get_current_user():
    return _make_mock_user()


async def _mock_get_current_client():
    client = MagicMock()
    client.sub = "00000000-0000-0000-0000-000000000002"
    client.type = "client"
    client.org = "00000000-0000-0000-0000-000000000001"
    client.roles = []
    client.scopes = ["automation:rule"]
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
    assert data["service"] == "automation-service"


# ============================================
# Test 2: Auth Required - Rules endpoint
# ============================================
def test_rules_list_requires_auth():
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
    response = c.get("/api/v1/automation/rules")
    assert response.status_code == 401


# ============================================
# Test 3: Rule CRUD - Create
# ============================================
def test_create_rule(client, auth_headers):
    mock_rule = _make_mock_rule()

    import src.api.rules as rules_module
    rules_module.create_rule = AsyncMock(return_value=mock_rule)

    response = client.post(
        "/api/v1/automation/rules",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Auto Notify Rule",
            "trigger_type": "schedule",
            "condition": {"field": "status", "operator": "eq", "value": "pending"},
            "action": {
                "type": "notify",
                "config": {"channel": "email"},
            },
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Rule"


# ============================================
# Test 4: Rule CRUD - Get
# ============================================
def test_get_rule(client, auth_headers):
    rule_id = uuid4()
    mock_rule = _make_mock_rule(rule_id=rule_id)

    import src.api.rules as rules_module
    rules_module.get_rule_by_id = AsyncMock(return_value=mock_rule)

    response = client.get(
        f"/api/v1/automation/rules/{rule_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(rule_id)


# ============================================
# Test 5: Rule CRUD - Update
# ============================================
def test_update_rule(client, auth_headers):
    rule_id = uuid4()
    mock_rule = _make_mock_rule(rule_id=rule_id)

    import src.api.rules as rules_module
    rules_module.update_rule = AsyncMock(return_value=mock_rule)

    response = client.put(
        f"/api/v1/automation/rules/{rule_id}",
        json={"name": "Updated Rule Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 6: Rule CRUD - Delete
# ============================================
def test_delete_rule(client, auth_headers):
    rule_id = uuid4()

    import src.api.rules as rules_module
    rules_module.delete_rule = AsyncMock(return_value=True)

    response = client.delete(
        f"/api/v1/automation/rules/{rule_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 7: Task CRUD - Create + Trigger Now
# ============================================
def test_create_task_and_trigger(client, auth_headers):
    mock_task = _make_mock_task()
    mock_run = _make_mock_task_run(task_id=mock_task.id)

    import src.api.tasks as tasks_module
    tasks_module.create_task = AsyncMock(return_value=mock_task)
    tasks_module.trigger_task_now = AsyncMock(return_value=mock_run)

    response = client.post(
        "/api/v1/automation/tasks",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Nightly Backup",
            "cron_expression": "0 2 * * *",
            "action_type": "execute",
            "action_config": {"script": "backup.sh"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Task"

    response2 = client.post(
        f"/api/v1/automation/tasks/{mock_task.id}/trigger",
        headers=auth_headers,
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True
    assert data2["data"]["status"] == "completed"


# ============================================
# Test 8: Task Run History
# ============================================
def test_get_task_run_history(client, auth_headers):
    task_id = uuid4()
    mock_task = _make_mock_task(task_id=task_id)
    mock_runs = [_make_mock_task_run(task_id=task_id) for _ in range(3)]

    import src.api.tasks as tasks_module
    tasks_module.get_task_by_id = AsyncMock(return_value=mock_task)
    tasks_module.get_task_run_history = AsyncMock(return_value=mock_runs)

    response = client.get(
        f"/api/v1/automation/tasks/{task_id}/history",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3


# ============================================
# Test 9: Trigger CRUD - Create + Enable/Disable
# ============================================
def test_create_trigger_enable_disable(client, auth_headers):
    mock_trigger = _make_mock_trigger()

    import src.api.triggers as triggers_module
    triggers_module.create_trigger = AsyncMock(return_value=mock_trigger)
    triggers_module.enable_trigger = AsyncMock(return_value=mock_trigger)
    triggers_module.disable_trigger = AsyncMock(return_value=mock_trigger)

    response = client.post(
        "/api/v1/automation/triggers",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "IoT Device Alert Trigger",
            "event_type": "iot.device.alert",
            "filter_conditions": {"device_type": "crane"},
            "action_config": {"type": "webhook", "url": "https://example.com/hook"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mock Trigger"

    response2 = client.post(
        f"/api/v1/automation/triggers/{mock_trigger.id}/disable",
        headers=auth_headers,
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True

    response3 = client.post(
        f"/api/v1/automation/triggers/{mock_trigger.id}/enable",
        headers=auth_headers,
    )
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["success"] is True


# ============================================
# Test 10: Trigger CRUD - List
# ============================================
def test_list_triggers(client, auth_headers):
    mock_trigger = _make_mock_trigger()

    import src.api.triggers as triggers_module
    triggers_module.get_triggers_paginated = AsyncMock(return_value=([mock_trigger], 1))

    response = client.get(
        "/api/v1/automation/triggers?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1


# ============================================
# Test 11: Rule enable/disable
# ============================================
def test_rule_enable_disable(client, auth_headers):
    rule_id = uuid4()
    mock_rule = _make_mock_rule(rule_id=rule_id)

    import src.api.rules as rules_module
    rules_module.enable_rule = AsyncMock(return_value=mock_rule)
    rules_module.disable_rule = AsyncMock(return_value=mock_rule)

    response = client.post(
        f"/api/v1/automation/rules/{rule_id}/enable",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    response2 = client.post(
        f"/api/v1/automation/rules/{rule_id}/disable",
        headers=auth_headers,
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True


# ============================================
# Test 12: Rule test execution
# ============================================
def test_rule_test_execution(client, auth_headers):
    rule_id = uuid4()
    test_result = {
        "rule_id": rule_id,
        "rule_name": "Test Rule",
        "matched": True,
        "action_type": "notify",
        "action_result": {"executed": True, "simulated": True},
    }

    import src.api.rules as rules_module
    rules_module.test_rule_execution = AsyncMock(return_value=test_result)

    response = client.post(
        f"/api/v1/automation/rules/{rule_id}/test",
        json={"input_data": {"status": "pending"}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["matched"] is True


# ============================================
# Test 13: Rule list with pagination
# ============================================
def test_list_rules(client, auth_headers):
    mock_rule = _make_mock_rule()

    import src.api.rules as rules_module
    rules_module.get_rules_paginated = AsyncMock(return_value=([mock_rule], 1))

    response = client.get(
        "/api/v1/automation/rules?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1
    assert len(data["data"]["rules"]) == 1


# ============================================
# Test 14: Rule list with filter params
# ============================================
def test_list_rules_filter(client, auth_headers):
    mock_rule = _make_mock_rule()

    import src.api.rules as rules_module
    rules_module.get_rules_paginated = AsyncMock(return_value=([mock_rule], 1))

    response = client.get(
        "/api/v1/automation/rules?trigger_type=schedule&is_active=true",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    rules_module.get_rules_paginated.assert_called_once()
    call_kwargs = rules_module.get_rules_paginated.call_args.kwargs
    assert call_kwargs["trigger_type"] == "schedule"
    assert call_kwargs["is_active"] is True


# ============================================
# Test 15: Rule not found - GET
# ============================================
def test_get_rule_not_found(client, auth_headers):
    rule_id = uuid4()

    import src.api.rules as rules_module
    rules_module.get_rule_by_id = AsyncMock(return_value=None)

    response = client.get(
        f"/api/v1/automation/rules/{rule_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "RULE_NOT_FOUND"


# ============================================
# Test 16: Rule not found - PUT
# ============================================
def test_update_rule_not_found(client, auth_headers):
    rule_id = uuid4()

    import src.api.rules as rules_module
    rules_module.update_rule = AsyncMock(return_value=None)

    response = client.put(
        f"/api/v1/automation/rules/{rule_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "RULE_NOT_FOUND"


# ============================================
# Test 17: Rule not found - DELETE
# ============================================
def test_delete_rule_not_found(client, auth_headers):
    rule_id = uuid4()

    import src.api.rules as rules_module
    rules_module.delete_rule = AsyncMock(return_value=False)

    response = client.delete(
        f"/api/v1/automation/rules/{rule_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "RULE_NOT_FOUND"


# ============================================
# Test 18: Rule enable not found
# ============================================
def test_enable_rule_not_found(client, auth_headers):
    rule_id = uuid4()

    import src.api.rules as rules_module
    rules_module.enable_rule = AsyncMock(return_value=None)

    response = client.post(
        f"/api/v1/automation/rules/{rule_id}/enable",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "RULE_NOT_FOUND"


# ============================================
# Test 19: Task list with pagination
# ============================================
def test_list_tasks(client, auth_headers):
    mock_task = _make_mock_task()

    import src.api.tasks as tasks_module
    tasks_module.get_tasks_paginated = AsyncMock(return_value=([mock_task], 1))

    response = client.get(
        "/api/v1/automation/tasks?page=1&per_page=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1
    assert len(data["data"]["tasks"]) == 1


# ============================================
# Test 20: Task individual GET
# ============================================
def test_get_task(client, auth_headers):
    task_id = uuid4()
    mock_task = _make_mock_task(task_id=task_id)

    import src.api.tasks as tasks_module
    tasks_module.get_task_by_id = AsyncMock(return_value=mock_task)

    response = client.get(
        f"/api/v1/automation/tasks/{task_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(task_id)


# ============================================
# Test 21: Task update
# ============================================
def test_update_task(client, auth_headers):
    task_id = uuid4()
    mock_task = _make_mock_task(task_id=task_id)

    import src.api.tasks as tasks_module
    tasks_module.update_task = AsyncMock(return_value=mock_task)

    response = client.put(
        f"/api/v1/automation/tasks/{task_id}",
        json={"name": "Updated Task", "cron_expression": "0 3 * * *"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 22: Task delete
# ============================================
def test_delete_task(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.delete_task = AsyncMock(return_value=True)

    response = client.delete(
        f"/api/v1/automation/tasks/{task_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 23: Task not found - GET
# ============================================
def test_get_task_not_found(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.get_task_by_id = AsyncMock(return_value=None)

    response = client.get(
        f"/api/v1/automation/tasks/{task_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TASK_NOT_FOUND"


# ============================================
# Test 24: Task not found - PUT
# ============================================
def test_update_task_not_found(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.update_task = AsyncMock(return_value=None)

    response = client.put(
        f"/api/v1/automation/tasks/{task_id}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TASK_NOT_FOUND"


# ============================================
# Test 25: Task not found - DELETE
# ============================================
def test_delete_task_not_found(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.delete_task = AsyncMock(return_value=False)

    response = client.delete(
        f"/api/v1/automation/tasks/{task_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TASK_NOT_FOUND"


# ============================================
# Test 26: Trigger task not found
# ============================================
def test_trigger_task_not_found(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.trigger_task_now = AsyncMock(return_value=None)

    response = client.post(
        f"/api/v1/automation/tasks/{task_id}/trigger",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TASK_NOT_FOUND"


# ============================================
# Test 27: Task history not found
# ============================================
def test_task_history_not_found(client, auth_headers):
    task_id = uuid4()

    import src.api.tasks as tasks_module
    tasks_module.get_task_by_id = AsyncMock(return_value=None)

    response = client.get(
        f"/api/v1/automation/tasks/{task_id}/history",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TASK_NOT_FOUND"


# ============================================
# Test 28: Trigger individual GET
# ============================================
def test_get_trigger(client, auth_headers):
    trigger_id = uuid4()
    mock_trigger = _make_mock_trigger(trigger_id=trigger_id)

    import src.api.triggers as triggers_module
    triggers_module.get_trigger_by_id = AsyncMock(return_value=mock_trigger)

    response = client.get(
        f"/api/v1/automation/triggers/{trigger_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(trigger_id)


# ============================================
# Test 29: Trigger update
# ============================================
def test_update_trigger(client, auth_headers):
    trigger_id = uuid4()
    mock_trigger = _make_mock_trigger(trigger_id=trigger_id)

    import src.api.triggers as triggers_module
    triggers_module.update_trigger = AsyncMock(return_value=mock_trigger)

    response = client.put(
        f"/api/v1/automation/triggers/{trigger_id}",
        json={"name": "Updated Trigger"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 30: Trigger delete
# ============================================
def test_delete_trigger(client, auth_headers):
    trigger_id = uuid4()

    import src.api.triggers as triggers_module
    triggers_module.delete_trigger = AsyncMock(return_value=True)

    response = client.delete(
        f"/api/v1/automation/triggers/{trigger_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================
# Test 31: Trigger not found - GET
# ============================================
def test_get_trigger_not_found(client, auth_headers):
    trigger_id = uuid4()

    import src.api.triggers as triggers_module
    triggers_module.get_trigger_by_id = AsyncMock(return_value=None)

    response = client.get(
        f"/api/v1/automation/triggers/{trigger_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TRIGGER_NOT_FOUND"


# ============================================
# Test 32: Trigger not found - PUT
# ============================================
def test_update_trigger_not_found(client, auth_headers):
    trigger_id = uuid4()

    import src.api.triggers as triggers_module
    triggers_module.update_trigger = AsyncMock(return_value=None)

    response = client.put(
        f"/api/v1/automation/triggers/{trigger_id}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TRIGGER_NOT_FOUND"


# ============================================
# Test 33: Trigger not found - DELETE
# ============================================
def test_delete_trigger_not_found(client, auth_headers):
    trigger_id = uuid4()

    import src.api.triggers as triggers_module
    triggers_module.delete_trigger = AsyncMock(return_value=False)

    response = client.delete(
        f"/api/v1/automation/triggers/{trigger_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "TRIGGER_NOT_FOUND"
