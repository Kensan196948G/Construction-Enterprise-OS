"""Security service API tests."""

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
TEST_INCIDENT_ID = uuid.uuid4()
TEST_VULN_ID = uuid.uuid4()
TEST_POLICY_ID = uuid.uuid4()

VALID_TOKEN_PAYLOAD = {
    "sub": str(TEST_USER_ID),
    "type": "user",
    "org": str(TEST_ORG_ID),
    "roles": ["security_admin", "admin"],
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


class MockIncident:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_INCIDENT_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.title = kwargs.get("title", "Test Incident")
        self.description = kwargs.get("description", None)
        self.severity = kwargs.get("severity", "high")
        self.incident_type = kwargs.get("incident_type", "unauthorized_access")
        self.status = kwargs.get("status", "open")
        self.source_ip = kwargs.get("source_ip", None)
        self.affected_systems = kwargs.get("affected_systems", None)
        self.detected_by = kwargs.get("detected_by", None)
        self.assigned_to = kwargs.get("assigned_to", None)
        self.resolution = kwargs.get("resolution", None)
        self.resolved_at = kwargs.get("resolved_at", None)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())
        self.updates = kwargs.get("updates", [])


class MockIncidentUpdate:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.incident_id = kwargs.get("incident_id", TEST_INCIDENT_ID)
        self.user_id = kwargs.get("user_id", TEST_USER_ID)
        self.update_type = kwargs.get("update_type", "note")
        self.content = kwargs.get("content", "Test update")
        self.created_at = kwargs.get("created_at", _utcnow())


class MockVulnerability:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_VULN_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.title = kwargs.get("title", "Test Vulnerability")
        self.description = kwargs.get("description", None)
        self.severity = kwargs.get("severity", "critical")
        self.cve_id = kwargs.get("cve_id", None)
        self.cvss_score = kwargs.get("cvss_score", None)
        self.affected_component = kwargs.get("affected_component", None)
        self.status = kwargs.get("status", "open")
        self.remediation = kwargs.get("remediation", None)
        self.discovered_at = kwargs.get("discovered_at", _utcnow())
        self.fixed_at = kwargs.get("fixed_at", None)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())


class MockPolicy:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_POLICY_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.name = kwargs.get("name", "Access Control Policy")
        self.description = kwargs.get("description", None)
        self.category = kwargs.get("category", "access_control")
        self.content = kwargs.get("content", "Policy content")
        self.version = kwargs.get("version", 1)
        self.status = kwargs.get("status", "active")
        self.effective_date = kwargs.get("effective_date", None)
        self.review_date = kwargs.get("review_date", None)
        self.approved_by = kwargs.get("approved_by", None)
        self.created_at = kwargs.get("created_at", _utcnow())
        self.updated_at = kwargs.get("updated_at", _utcnow())


class MockAudit:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.audit_type = kwargs.get("audit_type", "vulnerability_scan")
        self.status = kwargs.get("status", "completed")
        self.findings = kwargs.get("findings", None)
        self.recommendations = kwargs.get("recommendations", None)
        self.auditor = kwargs.get("auditor", None)
        self.scheduled_date = kwargs.get("scheduled_date", None)
        self.completed_date = kwargs.get("completed_date", None)
        self.created_at = kwargs.get("created_at", _utcnow())


# ═══════════════════════════════════════════════
# Test 1: Health check
# ═══════════════════════════════════════════════

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "security-service"


# ═══════════════════════════════════════════════
# Test 2-5: Auth required for endpoints
# ═══════════════════════════════════════════════

def test_incidents_require_auth(client):
    response = client.get("/api/v1/security/incidents")
    assert response.status_code == 401


def test_vulnerabilities_require_auth(client):
    response = client.get("/api/v1/security/vulnerabilities")
    assert response.status_code == 401


def test_policies_require_auth(client):
    response = client.get("/api/v1/security/policies")
    assert response.status_code == 401


def test_dashboard_requires_auth(client):
    response = client.get("/api/v1/security/dashboard")
    assert response.status_code == 401


# ═══════════════════════════════════════════════
# Test 6: Incident CRUD + status transitions
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

    client = TestClient(app)
    response = client.post(
        "/api/v1/security/incidents",
        json={
            "organization_id": str(TEST_ORG_ID),
            "title": "Unauthorized Access Detected",
            "severity": "high",
            "incident_type": "unauthorized_access",
            "description": "Multiple failed login attempts",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Unauthorized Access Detected"
    assert data["data"]["severity"] == "high"
    assert data["data"]["status"] == "open"


@patch("src.middleware.auth.jwt")
def test_list_incidents(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    inc1 = MockIncident(
        id=uuid.uuid4(), title="Incident 1", severity="critical", status="open"
    )
    inc2 = MockIncident(
        id=uuid.uuid4(), title="Incident 2", severity="medium", status="investigating"
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
        "/api/v1/security/incidents",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_get_incident_with_updates(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    update = MockIncidentUpdate(
        id=1,
        update_type="note",
        content="Investigation started",
    )
    incident = MockIncident(
        id=TEST_INCIDENT_ID,
        title="Phishing Attack",
        severity="high",
        status="investigating",
        updates=[update],
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([incident]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Phishing Attack"
    assert len(data["updates"]) == 1
    assert data["updates"][0]["update_type"] == "note"


@patch("src.middleware.auth.jwt")
def test_update_incident_status_transition(mock_jwt, app):
    """Test status flow: open → investigating → contained → resolved → closed"""
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    incident = MockIncident(
        id=TEST_INCIDENT_ID,
        title="DDoS Attack",
        severity="critical",
        status="open",
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([incident]))
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)

    # open → investigating
    response = client.put(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        json={"status": "investigating"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "investigating"

    # investigating → contained
    response = client.put(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        json={"status": "contained"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "contained"

    # contained → resolved
    response = client.put(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        json={"status": "resolved", "resolution": "DDoS mitigated"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "resolved"

    # resolved → closed
    response = client.put(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        json={"status": "closed", "resolution": "Final review complete"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert incident.status == "closed"


@patch("src.middleware.auth.jwt")
def test_add_incident_update(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    incident = MockIncident(id=TEST_INCIDENT_ID, status="investigating")

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
    response = client.post(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}/updates",
        json={"update_type": "note", "content": "Collecting forensic data"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 201


@patch("src.middleware.auth.jwt")
def test_update_incident_not_found(mock_jwt, app):
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
    response = client.put(
        f"/api/v1/security/incidents/{TEST_INCIDENT_ID}",
        json={"status": "closed"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 404


@patch("src.middleware.auth.jwt")
def test_get_active_incident_count(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([5]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/security/incidents/active",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["data"]["active_incidents"] == 5


# ═══════════════════════════════════════════════
# Test 12: Vulnerability CRUD
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_vulnerability_success(mock_jwt, app):
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
        "/api/v1/security/vulnerabilities",
        json={
            "organization_id": str(TEST_ORG_ID),
            "title": "SQL Injection in Login Page",
            "severity": "critical",
            "cve_id": "CVE-2024-1234",
            "cvss_score": 9.8,
            "affected_component": "login.php",
            "description": "Unsanitized input allows SQL injection",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "SQL Injection in Login Page"
    assert data["data"]["severity"] == "critical"
    assert data["data"]["cve_id"] == "CVE-2024-1234"


@patch("src.middleware.auth.jwt")
def test_list_vulnerabilities(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    v1 = MockVulnerability(
        id=uuid.uuid4(), title="Vuln 1", severity="high", status="open"
    )
    v2 = MockVulnerability(
        id=uuid.uuid4(), title="Vuln 2", severity="low", status="fixed"
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([v1, v2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/security/vulnerabilities?severity=high",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_update_vulnerability_status(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    vuln = MockVulnerability(
        id=TEST_VULN_ID,
        title="XSS Vulnerability",
        severity="high",
        status="open",
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([vuln]))
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.put(
        f"/api/v1/security/vulnerabilities/{TEST_VULN_ID}",
        json={"status": "fixed", "remediation": "Applied output encoding"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert vuln.status == "fixed"
    assert vuln.remediation == "Applied output encoding"


@patch("src.middleware.auth.jwt")
def test_update_vulnerability_not_found(mock_jwt, app):
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
    response = client.put(
        f"/api/v1/security/vulnerabilities/{TEST_VULN_ID}",
        json={"status": "fixed"},
        headers=_make_auth_header(),
    )
    assert response.status_code == 404


@patch("src.middleware.auth.jwt")
def test_get_open_vulnerabilities_by_severity(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    rows = [("critical", 2), ("high", 5), ("medium", 3), ("low", 10)]
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult(rows))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/security/vulnerabilities/open",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()["data"]["open_vulnerabilities"]
    assert data["critical"] == 2
    assert data["high"] == 5


# ═══════════════════════════════════════════════
# Test 17-19: Policy management
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_policy_success(mock_jwt, app):
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
        "/api/v1/security/policies",
        json={
            "organization_id": str(TEST_ORG_ID),
            "name": "Access Control Policy v2",
            "category": "access_control",
            "content": "All access must be authenticated and authorized.",
            "description": "Updated access control requirements",
            "effective_date": "2024-01-01",
            "review_date": "2025-01-01",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "Access Control Policy v2"
    assert data["data"]["category"] == "access_control"


@patch("src.middleware.auth.jwt")
def test_get_policy_content(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    policy = MockPolicy(
        id=TEST_POLICY_ID,
        name="Data Protection Policy",
        category="data_protection",
        content="All PII must be encrypted at rest and in transit.",
        status="active",
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([policy]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        f"/api/v1/security/policies/{TEST_POLICY_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Data Protection Policy"
    assert data["content"] == "All PII must be encrypted at rest and in transit."


@patch("src.middleware.auth.jwt")
def test_list_policies(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    p1 = MockPolicy(
        id=uuid.uuid4(), name="Policy A", category="access_control", status="active"
    )
    p2 = MockPolicy(
        id=uuid.uuid4(), name="Policy B", category="data_protection", status="draft"
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([p1, p2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/security/policies",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_update_policy(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    policy = MockPolicy(
        id=TEST_POLICY_ID,
        name="Old Policy",
        category="access_control",
        content="Old content",
        status="active",
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([policy]))
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.put(
        f"/api/v1/security/policies/{TEST_POLICY_ID}",
        json={
            "name": "Updated Policy",
            "content": "Updated content with new requirements",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert policy.name == "Updated Policy"
    assert policy.content == "Updated content with new requirements"


@patch("src.middleware.auth.jwt")
def test_review_policy(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    policy = MockPolicy(
        id=TEST_POLICY_ID,
        name="Reviewable Policy",
        category="compliance",
        content="Compliance requirements",
        version=1,
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([policy]))
    db_mock.add = MagicMock()
    db_mock.flush = AsyncMock()
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        f"/api/v1/security/policies/{TEST_POLICY_ID}/review",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert policy.version == 2


# ═══════════════════════════════════════════════
# Test 22: Dashboard stats correctness
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_dashboard_statistics(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    inc_severity = [("critical", 1), ("high", 2), ("medium", 5), ("low", 3)]
    vuln_severity = [("critical", 0), ("high", 3), ("medium", 8), ("low", 15)]
    policies_due = 3
    recent = [
        MockIncident(id=uuid.uuid4(), title="Recent Incident 1", severity="high", status="investigating"),
        MockIncident(id=uuid.uuid4(), title="Recent Incident 2", severity="medium", status="open"),
    ]
    audit = MockAudit(status="completed")

    call_count = 0

    async def mock_execute(statement):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockScalarResult(inc_severity)
        elif call_count == 2:
            return MockScalarResult(vuln_severity)
        elif call_count == 3:
            return MockScalarResult([policies_due])
        elif call_count == 4:
            return MockScalarResult(recent)
        elif call_count == 5:
            return MockScalarResult([audit])
        return MockScalarResult([])

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=mock_execute)
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/security/dashboard",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["open_incidents"]["critical"] == 1
    assert data["open_incidents"]["high"] == 2
    assert data["open_incidents"]["medium"] == 5
    assert data["open_incidents"]["low"] == 3
    assert data["open_vulnerabilities"]["critical"] == 0
    assert data["open_vulnerabilities"]["high"] == 3
    assert data["open_vulnerabilities"]["medium"] == 8
    assert data["open_vulnerabilities"]["low"] == 15
    assert data["policies_due_review"] == 3
    assert data["latest_audit_status"] == "completed"
    assert len(data["recent_incidents"]) == 2
