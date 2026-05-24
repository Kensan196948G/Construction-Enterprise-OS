"""ワークフローAPI テスト"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db


def _utcnow():
    return datetime.now(timezone.utc)

TEST_USER_ID = uuid.uuid4()
TEST_ORG_ID = uuid.uuid4()
TEST_DEF_ID = uuid.uuid4()
TEST_INST_ID = uuid.uuid4()

VALID_TOKEN_PAYLOAD = {
    "sub": str(TEST_USER_ID),
    "type": "user",
    "org": str(TEST_ORG_ID),
    "roles": ["site_manager", "department_head"],
    "scopes": [],
}


def _make_auth_header() -> dict:
    import base64
    import json

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(VALID_TOKEN_PAYLOAD).encode()
    ).decode().rstrip("=")
    header_b64 = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).decode().rstrip("=")
    signature = "fake_signature"
    token = f"{header_b64}.{payload_b64}.{signature}"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def app():
    _app = create_app()
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


# ——— Health Check ———


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ——— Auth Required ———


def test_definitions_require_auth(client):
    response = client.get("/api/v1/workflow/definitions")
    assert response.status_code == 401


def test_instances_require_auth(client):
    response = client.get("/api/v1/workflow/instances")
    assert response.status_code == 401


def test_create_definition_requires_auth(client):
    response = client.post("/api/v1/workflow/definitions", json={})
    assert response.status_code == 401


def test_create_instance_requires_auth(client):
    response = client.post("/api/v1/workflow/instances", json={})
    assert response.status_code == 401


# ——— Workflow Definition CRUD ———


class MockScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self


class MockDefinition:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_DEF_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.name = kwargs.get("name", "テスト定義")
        self.description = kwargs.get("description", None)
        self.category = kwargs.get("category", "ringi")
        self.steps = kwargs.get("steps", [{"order": 1, "role": "site_manager", "required": True}])
        self.is_active = kwargs.get("is_active", True)
        self.created_by = kwargs.get("created_by", TEST_USER_ID)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())


class MockInstance:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_INST_ID)
        self.definition_id = kwargs.get("definition_id", TEST_DEF_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.title = kwargs.get("title", "テスト稟議")
        self.description = kwargs.get("description", None)
        self.category = kwargs.get("category", "ringi")
        self.status = kwargs.get("status", "draft")
        self.priority = kwargs.get("priority", "normal")
        self.reference_type = kwargs.get("reference_type", None)
        self.reference_id = kwargs.get("reference_id", None)
        self.metadata_ = kwargs.get("metadata_", {})
        self.submitted_by = kwargs.get("submitted_by", TEST_USER_ID)
        self.submitted_at = kwargs.get("submitted_at", None)
        self.completed_at = kwargs.get("completed_at", None)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())
        self.approvals = kwargs.get("approvals", [])


class MockApproval:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.instance_id = kwargs.get("instance_id", TEST_INST_ID)
        self.step_order = kwargs.get("step_order", 1)
        self.approver_id = kwargs.get("approver_id", None)
        self.approver_role = kwargs.get("approver_role", "site_manager")
        self.status = kwargs.get("status", "pending")
        self.comment = kwargs.get("comment", None)
        self.approved_at = kwargs.get("approved_at", None)
        self.created_at = kwargs.get("created_at", _utcnow())


@patch("src.middleware.auth.jwt")
def test_list_definitions_filtered(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_def1 = MockDefinition(
        id=uuid.uuid4(), name="一般稟議", category="ringi",
        steps=[{"order": 1, "role": "site_manager", "required": True}],
    )
    mock_def2 = MockDefinition(
        id=uuid.uuid4(), name="安全許可", category="safety_approval",
        steps=[{"order": 1, "role": "safety_officer", "required": True}],
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_def1, mock_def2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/workflow/definitions?category=ringi",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


# Patch-based tests for full workflow flow
@patch("src.middleware.auth.jwt")
def test_health_check_with_mock(mock_jwt, client):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD
    response = client.get("/health")
    assert response.status_code == 200


@patch("src.middleware.auth.jwt")
def test_list_definitions_empty(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    app.dependency_overrides[get_db] = lambda: db_mock

    client = TestClient(app)
    response = client.get("/api/v1/workflow/definitions", headers=_make_auth_header())
    assert response.status_code == 200
    assert response.json()["data"] == []


@patch("src.middleware.auth.jwt")
def test_create_definition_success(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/workflow/definitions",
        json={
            "organization_id": str(TEST_ORG_ID),
            "name": "一般稟議",
            "category": "ringi",
            "steps": [{"order": 1, "role": "site_manager", "required": True}],
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "一般稟議"


@patch("src.middleware.auth.jwt")
def test_create_instance_auto_creates_approvals(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_def = MockDefinition(
        id=TEST_DEF_ID,
        category="ringi",
        steps=[
            {"order": 1, "role": "site_manager", "required": True},
            {"order": 2, "role": "department_head", "required": True},
        ],
    )
    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="draft",
    )
    mock_approval1 = MockApproval(instance_id=TEST_INST_ID, step_order=1, approver_role="site_manager")
    mock_approval2 = MockApproval(instance_id=TEST_INST_ID, step_order=2, approver_role="department_head")
    mock_instance.approvals = [mock_approval1, mock_approval2]

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_instance]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    call_count = 0

    async def mock_execute_side_effect(statement):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockScalarResult([mock_def])
        return MockScalarResult([mock_instance])

    db_mock.execute = AsyncMock(side_effect=mock_execute_side_effect)

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/workflow/instances",
        json={
            "definition_id": str(TEST_DEF_ID),
            "organization_id": str(TEST_ORG_ID),
            "title": "テスト稟議",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["status"] == "draft"
    assert len(data["data"]["approvals"]) == 2


@patch("src.middleware.auth.jwt")
def test_submit_instance(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="draft",
    )
    mock_instance.approvals = []

    mock_submitted = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_submitted.submitted_at = _utcnow()

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_instance]))
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/workflow/instances/{TEST_INST_ID}/submit",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "in_progress"


@patch("src.middleware.auth.jwt")
def test_approve_step(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_approval = MockApproval(
        instance_id=TEST_INST_ID, step_order=1,
        approver_role="site_manager", status="pending",
    )
    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_instance.approvals = [mock_approval]

    mock_post_approve = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="approved",
    )
    mock_post_approve.completed_at = _utcnow()
    mock_post_approve.approvals = [
        MockApproval(
            instance_id=TEST_INST_ID, step_order=1,
            approver_role="site_manager", status="approved",
            approver_id=TEST_USER_ID,
        )
    ]

    db_mock = AsyncMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    call_count = 0

    async def mock_execute_side_effect(statement):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockScalarResult([mock_instance])
        if call_count == 2:
            return MockScalarResult([mock_approval])
        return MockScalarResult([])

    db_mock.execute = AsyncMock(side_effect=mock_execute_side_effect)

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/workflow/instances/{TEST_INST_ID}/approve?step_order=1",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200


@patch("src.middleware.auth.jwt")
def test_reject_step(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_approval = MockApproval(
        instance_id=TEST_INST_ID, step_order=1,
        approver_role="site_manager", status="pending",
    )
    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_instance.approvals = [mock_approval]

    db_mock = AsyncMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    call_count = 0

    async def mock_execute_side_effect(statement):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockScalarResult([mock_instance])
        if call_count == 2:
            return MockScalarResult([mock_approval])
        return MockScalarResult([])

    db_mock.execute = AsyncMock(side_effect=mock_execute_side_effect)

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/workflow/instances/{TEST_INST_ID}/reject?step_order=1",
        json={"comment": "不備あり"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200


@patch("src.middleware.auth.jwt")
def test_cancel_instance(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_instance.approvals = []

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_instance]))
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/workflow/instances/{TEST_INST_ID}/cancel",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200


@patch("src.middleware.auth.jwt")
def test_get_pending_approvals(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_approval = MockApproval(
        instance_id=TEST_INST_ID, step_order=1,
        approver_role="site_manager", status="pending",
    )
    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_instance.approvals = [mock_approval]

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_instance]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/workflow/instances/pending",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1


@patch("src.middleware.auth.jwt")
def test_get_instance_not_found(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        f"/api/v1/workflow/instances/{uuid.uuid4()}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 404


@patch("src.middleware.auth.jwt")
def test_get_history(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    mock_approval1 = MockApproval(
        instance_id=TEST_INST_ID, step_order=1,
        approver_role="site_manager", status="approved",
        approver_id=TEST_USER_ID,
    )
    mock_approval2 = MockApproval(
        instance_id=TEST_INST_ID, step_order=2,
        approver_role="department_head", status="pending",
    )
    mock_instance = MockInstance(
        id=TEST_INST_ID,
        category="ringi",
        status="in_progress",
    )
    mock_instance.approvals = [mock_approval1, mock_approval2]

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([mock_instance]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        f"/api/v1/workflow/instances/{TEST_INST_ID}/history",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
