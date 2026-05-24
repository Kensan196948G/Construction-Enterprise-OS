"""Safety service API tests."""

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
TEST_INSPECTION_ID = uuid.uuid4()
TEST_HAZARD_ID = uuid.uuid4()
TEST_INCIDENT_ID = uuid.uuid4()

VALID_TOKEN_PAYLOAD = {
    "sub": str(TEST_USER_ID),
    "type": "user",
    "org": str(TEST_ORG_ID),
    "roles": ["safety_admin", "admin"],
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
    mock_db.add = MagicMock()
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


class MockScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalar(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self


class MockInspection:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_INSPECTION_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.project_id = kwargs.get("project_id", None)
        self.site_id = kwargs.get("site_id", None)
        self.title = kwargs.get("title", "Test Inspection")
        self.inspection_type = kwargs.get("inspection_type", "daily")
        self.status = kwargs.get("status", "scheduled")
        self.inspector_id = kwargs.get("inspector_id", TEST_USER_ID)
        self.inspection_date = kwargs.get("inspection_date", None)
        self.location = kwargs.get("location", None)
        self.findings = kwargs.get("findings", None)
        self.corrective_actions = kwargs.get("corrective_actions", None)
        self.score = kwargs.get("score", None)
        self.is_safe = kwargs.get("is_safe", None)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())


class MockHazard:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_HAZARD_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.project_id = kwargs.get("project_id", None)
        self.site_id = kwargs.get("site_id", None)
        self.title = kwargs.get("title", "Test Hazard")
        self.description = kwargs.get("description", "Hazard description")
        self.hazard_type = kwargs.get("hazard_type", "fall")
        self.risk_level = kwargs.get("risk_level", "high")
        self.severity = kwargs.get("severity", "severe")
        self.status = kwargs.get("status", "reported")
        self.location = kwargs.get("location", None)
        self.reported_by = kwargs.get("reported_by", TEST_USER_ID)
        self.assigned_to = kwargs.get("assigned_to", None)
        self.mitigation = kwargs.get("mitigation", None)
        self.resolved_at = kwargs.get("resolved_at", None)
        self.created_at = kwargs.get("created_at", _utcnow())


class MockIncident:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_INCIDENT_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.project_id = kwargs.get("project_id", None)
        self.site_id = kwargs.get("site_id", None)
        self.title = kwargs.get("title", "Test Incident")
        self.description = kwargs.get("description", "Incident description")
        self.incident_type = kwargs.get("incident_type", "injury")
        self.severity = kwargs.get("severity", "moderate")
        self.status = kwargs.get("status", "reported")
        self.incident_date = kwargs.get("incident_date", _utcnow())
        self.location = kwargs.get("location", None)
        self.injured_count = kwargs.get("injured_count", 0)
        self.fatality_count = kwargs.get("fatality_count", 0)
        self.root_cause = kwargs.get("root_cause", None)
        self.corrective_actions = kwargs.get("corrective_actions", None)
        self.reported_by = kwargs.get("reported_by", TEST_USER_ID)
        self.investigated_by = kwargs.get("investigated_by", None)
        self.resolved_at = kwargs.get("resolved_at", None)
        self.is_osha_reportable = kwargs.get("is_osha_reportable", False)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())


# ═══════════════════════════════════════════════
# Test 1: Health check
# ═══════════════════════════════════════════════

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "safety-service"


# ═══════════════════════════════════════════════
# Test 2-4: Auth required
# ═══════════════════════════════════════════════

def test_inspections_require_auth(client):
    response = client.get("/api/v1/safety/inspections")
    assert response.status_code == 401


def test_hazards_require_auth(client):
    response = client.get("/api/v1/safety/hazards")
    assert response.status_code == 401


def test_incidents_require_auth(client):
    response = client.get("/api/v1/safety/incidents")
    assert response.status_code == 401


# ═══════════════════════════════════════════════
# Test 5-7: Inspection CRUD + complete flow
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_inspection_success(mock_jwt, app):
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
        "/api/v1/safety/inspections",
        json={
            "organization_id": str(TEST_ORG_ID),
            "title": "Daily Site Inspection",
            "inspection_type": "daily",
            "inspector_id": str(TEST_USER_ID),
            "location": "Building A - Floor 3",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Daily Site Inspection"
    assert data["data"]["status"] == "scheduled"


@patch("src.middleware.auth.jwt")
def test_list_inspections(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    ins1 = MockInspection(
        id=uuid.uuid4(), title="Inspection 1", inspection_type="daily", status="scheduled"
    )
    ins2 = MockInspection(
        id=uuid.uuid4(), title="Inspection 2", inspection_type="weekly", status="completed"
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([ins1, ins2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/safety/inspections",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_inspection_complete_flow(mock_jwt, app):
    """Test full inspection lifecycle: scheduled → complete with pass/fail"""
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    inspection = MockInspection(
        id=TEST_INSPECTION_ID,
        title="Scaffolding Check",
        inspection_type="equipment",
        status="scheduled",
    )

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([inspection]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)

    # Update status to in_progress
    response = client.put(
        f"/api/v1/safety/inspections/{TEST_INSPECTION_ID}",
        json={"status": "in_progress"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert inspection.status == "in_progress"

    # Complete inspection: pass
    response = client.post(
        f"/api/v1/safety/inspections/{TEST_INSPECTION_ID}/complete",
        json={"is_safe": True, "findings": "All clear", "score": 95},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert inspection.status == "passed"
    assert inspection.is_safe is True
    assert inspection.score == 95


@patch("src.middleware.auth.jwt")
def test_inspection_complete_fail(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    inspection = MockInspection(
        id=uuid.uuid4(),
        title="Electrical Wiring Check",
        inspection_type="equipment",
        status="in_progress",
    )

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([inspection]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/safety/inspections/{inspection.id}/complete",
        json={
            "is_safe": False,
            "findings": "Exposed wiring in junction box",
            "corrective_actions": "Replace junction box cover",
            "score": 30,
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert inspection.status == "failed"
    assert inspection.is_safe is False
    assert inspection.score == 30


@patch("src.middleware.auth.jwt")
def test_inspection_not_found(mock_jwt, app):
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
        f"/api/v1/safety/inspections/{TEST_INSPECTION_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 404


# ═══════════════════════════════════════════════
# Test 10-12: Hazard report + status progression
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_hazard_success(mock_jwt, app):
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
        "/api/v1/safety/hazards",
        json={
            "organization_id": str(TEST_ORG_ID),
            "title": "Unsecured scaffolding at level 5",
            "description": "Scaffolding at level 5 missing guard rails",
            "hazard_type": "fall",
            "risk_level": "critical",
            "severity": "severe",
            "reported_by": str(TEST_USER_ID),
            "location": "Building B - Level 5",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Unsecured scaffolding at level 5"
    assert data["data"]["hazard_type"] == "fall"
    assert data["data"]["status"] == "reported"


@patch("src.middleware.auth.jwt")
def test_hazard_status_progression(mock_jwt, app):
    """Test: reported → assessed → mitigated → closed"""
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    hazard = MockHazard(
        id=TEST_HAZARD_ID,
        title="Chemical spill risk",
        hazard_type="chemical",
        risk_level="high",
        status="reported",
    )

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([hazard]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)

    # reported → assessed
    response = client.put(
        f"/api/v1/safety/hazards/{TEST_HAZARD_ID}",
        json={"status": "assessed", "risk_level": "medium"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert hazard.status == "assessed"
    assert hazard.risk_level == "medium"

    # assessed → mitigated
    response = client.put(
        f"/api/v1/safety/hazards/{TEST_HAZARD_ID}",
        json={"status": "mitigated", "mitigation": "Installed chemical containment"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert hazard.status == "mitigated"
    assert hazard.mitigation == "Installed chemical containment"

    # mitigated → closed
    response = client.put(
        f"/api/v1/safety/hazards/{TEST_HAZARD_ID}",
        json={"status": "closed"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert hazard.status == "closed"
    assert hazard.resolved_at is not None


# ═══════════════════════════════════════════════
# Test 13-14: Incident report flow
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_incident_success(mock_jwt, app):
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

    test_date = datetime(2024, 6, 15, 8, 30, 0, tzinfo=timezone.utc)
    client = TestClient(app)
    response = client.post(
        "/api/v1/safety/incidents",
        json={
            "organization_id": str(TEST_ORG_ID),
            "title": "Worker fell from scaffolding",
            "description": "Worker slipped and fell from 3m height",
            "incident_type": "injury",
            "severity": "severe",
            "incident_date": test_date.isoformat(),
            "injured_count": 1,
            "fatality_count": 0,
            "reported_by": str(TEST_USER_ID),
            "is_osha_reportable": True,
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Worker fell from scaffolding"
    assert data["data"]["incident_type"] == "injury"
    assert data["data"]["severity"] == "severe"
    assert data["data"]["injured_count"] == 1
    assert data["data"]["is_osha_reportable"] is True


@patch("src.middleware.auth.jwt")
def test_incident_investigation_flow(mock_jwt, app):
    """Test: reported → investigating → analyzed → resolved → closed"""
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    incident = MockIncident(
        id=TEST_INCIDENT_ID,
        title="Crane wire rope snapped",
        incident_type="equipment_failure",
        severity="catastrophic",
        status="reported",
        injured_count=0,
        fatality_count=0,
    )

    investigator_id = uuid.uuid4()

    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([incident]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)

    # reported → investigating
    response = client.put(
        f"/api/v1/safety/incidents/{TEST_INCIDENT_ID}",
        json={"status": "investigating", "investigated_by": str(investigator_id)},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "investigating"

    # investigating → analyzed
    response = client.put(
        f"/api/v1/safety/incidents/{TEST_INCIDENT_ID}",
        json={
            "status": "analyzed",
            "root_cause": "Wire rope fatigue due to overloading",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "analyzed"
    assert "fatigue" in incident.root_cause

    # analyzed → resolved
    response = client.put(
        f"/api/v1/safety/incidents/{TEST_INCIDENT_ID}",
        json={
            "status": "resolved",
            "corrective_actions": "Replaced wire rope, instituted load monitoring",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "resolved"
    assert incident.resolved_at is not None

    # resolved → closed
    response = client.put(
        f"/api/v1/safety/incidents/{TEST_INCIDENT_ID}",
        json={"status": "closed"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "closed"


# ═══════════════════════════════════════════════
# Test 15: Incident list with filters
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_list_incidents(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    inc1 = MockIncident(
        id=uuid.uuid4(), title="Fall injury", incident_type="injury", severity="moderate"
    )
    inc2 = MockIncident(
        id=uuid.uuid4(), title="Near miss", incident_type="near_miss", severity="minor"
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([inc1, inc2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/safety/incidents?incident_type=injury",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
