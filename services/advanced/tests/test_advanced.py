"""Advanced Service 結合テスト"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.main import create_app
from src.models.base import get_db
from src.middleware.auth import get_current_user


# ============================================
# ヘルパー
# ============================================
def _make_mock_user(sub="00000000-0000-0000-0000-000000000001"):
    user = MagicMock()
    user.sub = sub
    user.type = "user"
    user.org = "00000000-0000-0000-0000-000000000001"
    user.roles = ["admin"]
    user.scopes = []
    return user


def _make_mock_marine(mid=None):
    from datetime import datetime, timezone
    m = MagicMock()
    m.id = mid or uuid4()
    m.organization_id = uuid4()
    m.project_id = None
    m.name = "Test Breakwater"
    m.construction_type = "breakwater"
    m.status = "planning"
    m.water_depth = 15.0
    m.tide_info = {"type": "semi_diurnal"}
    m.wave_condition = {"height": 2.5, "period": 8.0, "direction": "SW"}
    m.equipment_deployed = ["dredger-1", "barge-2"]
    m.material_volume = 50000.0
    m.progress_percent = 25.0
    m.location = None
    m.start_date = None
    m.end_date = None
    m.supervisor_id = None
    m.created_at = datetime.now(timezone.utc)
    m.updated_at = datetime.now(timezone.utc)
    return m


def _make_mock_inspection(iid=None):
    from datetime import date, datetime, timezone
    m = MagicMock()
    m.id = iid or uuid4()
    m.organization_id = uuid4()
    m.asset_name = "Bridge A"
    m.asset_type = "bridge"
    m.inspection_method = "drone"
    m.ai_model_used = "crack-detection-v2"
    m.defect_type = "crack"
    m.severity = "moderate"
    m.confidence = 0.92
    m.defect_count = 3
    m.location = None
    m.image_keys = []
    m.ai_analysis = {}
    m.inspector_id = None
    m.inspection_date = date.today()
    m.requires_action = True
    m.created_at = datetime.now(timezone.utc)
    return m


def _make_mock_design_review(did=None):
    from datetime import datetime, timezone
    m = MagicMock()
    m.id = did or uuid4()
    m.organization_id = uuid4()
    m.project_id = None
    m.design_document_id = None
    m.review_type = "structural"
    m.status = "pending"
    m.ai_suggestions = []
    m.compliance_checks = {"standard": "ISO 19901", "passed": 10, "failed": 2, "violations": [{"clause": "4.2.1", "message": "不足"}]}
    m.reviewer_id = None
    m.reviewed_at = None
    m.created_at = datetime.now(timezone.utc)
    return m


def _make_mock_predictive(pid=None):
    from datetime import date, datetime, timezone
    m = MagicMock()
    m.id = pid or uuid4()
    m.organization_id = uuid4()
    m.asset_name = "Excavator Unit 5"
    m.asset_type = "heavy_machinery"
    m.model_type = "remaining_useful_life"
    m.status = "training"
    m.training_data_count = 10000
    m.accuracy = 0.95
    m.last_trained_at = None
    m.next_maintenance_predicted = date(2026, 6, 15)
    m.failure_probability = 0.15
    m.remaining_life_days = 180
    m.recommendations = []
    m.input_metrics = {}
    m.created_at = datetime.now(timezone.utc)
    m.updated_at = datetime.now(timezone.utc)
    return m


# ============================================
# Auth Fixture Helper
# ============================================
async def _mock_get_current_user():
    return _make_mock_user()


class MockScalarResult:
    def __init__(self, return_value=None, return_values=None):
        self._return_value = return_value
        self._return_values = return_values or []

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


# ============================================
# Fixtures
# ============================================
@pytest.fixture
def app():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockScalarResult()

    mock_db.execute = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    _app.dependency_overrides[get_current_user] = _mock_get_current_user
    return _app


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock-user-token"}


@pytest.fixture
def unauth_client():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockScalarResult()

    mock_db.execute = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = MagicMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    from fastapi.testclient import TestClient
    return TestClient(_app)


# ============================================
# 1. Health Check
# ============================================
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "advanced-service"


# ============================================
# 2-5. Auth Required Tests
# ============================================
def test_marine_create_requires_auth(unauth_client):
    response = unauth_client.post("/api/v1/advanced/marine", json={"name": "test"})
    assert response.status_code == 401


def test_inspection_requires_auth(unauth_client):
    response = unauth_client.post("/api/v1/advanced/inspections", json={"asset_name": "test"})
    assert response.status_code == 401


def test_design_review_requires_auth(unauth_client):
    response = unauth_client.post("/api/v1/advanced/design-reviews", json={"review_type": "structural"})
    assert response.status_code == 401


def test_predictive_requires_auth(unauth_client):
    response = unauth_client.post("/api/v1/advanced/predictive", json={"asset_name": "test"})
    assert response.status_code == 401


# ============================================
# 6-7. Marine Construction CRUD
# ============================================
def test_create_marine_construction(client, auth_headers):
    mock_marine = _make_mock_marine()

    import src.api.marine as marine_module
    marine_module.create_marine_construction = AsyncMock(return_value=mock_marine)

    response = client.post(
        "/api/v1/advanced/marine",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Test Breakwater",
            "construction_type": "breakwater",
            "water_depth": 15.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Breakwater"


def test_get_marine_construction(client, auth_headers):
    mid = uuid4()
    mock_marine = _make_mock_marine(mid=mid)

    import src.api.marine as marine_module
    marine_module.get_marine_construction_by_id = AsyncMock(return_value=mock_marine)

    response = client.get(f"/api/v1/advanced/marine/{mid}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["construction_type"] == "breakwater"


def test_update_marine_progress(client, auth_headers):
    mid = uuid4()
    mock_marine = _make_mock_marine(mid=mid)
    mock_marine.progress_percent = 75.0

    import src.api.marine as marine_module
    marine_module.update_marine_construction = AsyncMock(return_value=mock_marine)

    response = client.patch(
        f"/api/v1/advanced/marine/{mid}/progress",
        json={"progress_percent": 75.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["progress_percent"] == 75.0


def test_marine_construction_not_found(client, auth_headers):
    import src.api.marine as marine_module
    marine_module.get_marine_construction_by_id = AsyncMock(return_value=None)

    response = client.get(
        f"/api/v1/advanced/marine/{uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ============================================
# 8-9. Inspection Records CRUD
# ============================================
def test_create_inspection_record(client, auth_headers):
    mock_inspection = _make_mock_inspection()

    import src.api.inspections_ai as insp_module
    insp_module.create_inspection_record = AsyncMock(return_value=mock_inspection)

    response = client.post(
        "/api/v1/advanced/inspections",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "asset_name": "Bridge A",
            "asset_type": "bridge",
            "inspection_date": "2026-05-24",
            "severity": "moderate",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["asset_name"] == "Bridge A"


# ============================================
# 10. Defect Summary
# ============================================
def test_get_defect_summary(client, auth_headers):
    from datetime import date
    import src.api.inspections_ai as insp_module

    mock_insp1 = _make_mock_inspection(uuid4())
    mock_insp1.asset_type = "bridge"
    mock_insp1.severity = "moderate"
    mock_insp1.defect_type = "crack"
    mock_insp1.confidence = 0.92
    mock_insp1.requires_action = True

    mock_insp2 = _make_mock_inspection(uuid4())
    mock_insp2.asset_type = "tunnel"
    mock_insp2.severity = "critical"
    mock_insp2.defect_type = "deformation"
    mock_insp2.confidence = 0.88
    mock_insp2.requires_action = True

    insp_module.get_inspection_record_by_id = AsyncMock(return_value=None)
    insp_module.list_inspection_records = AsyncMock(
        return_value=([mock_insp1, mock_insp2], 2)
    )
    insp_module.get_defect_summary = AsyncMock(
        return_value={
            "total_inspections": 2,
            "by_severity": {"moderate": 1, "critical": 1},
            "by_asset_type": {"bridge": 1, "tunnel": 1},
            "by_defect_type": {"crack": 1, "deformation": 1},
            "requires_action_count": 2,
            "average_confidence": 0.9,
        }
    )

    response = client.get(
        "/api/v1/advanced/inspections/defect-summary",
        params={"organization_id": "00000000-0000-0000-0000-000000000001"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_inspections"] == 2
    assert data["data"]["requires_action_count"] == 2
    assert data["data"]["average_confidence"] == 0.9


# ============================================
# 11. AI Design Review CRUD
# ============================================
def test_create_design_review(client, auth_headers):
    mock_review = _make_mock_design_review()

    import src.api.design_review as dr_module
    dr_module.create_design_review = AsyncMock(return_value=mock_review)

    response = client.post(
        "/api/v1/advanced/design-reviews",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "review_type": "structural",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["review_type"] == "structural"


# ============================================
# 12. Compliance Report
# ============================================
def test_get_compliance_report(client, auth_headers):
    rid = uuid4()

    import src.api.design_review as dr_module
    dr_module.get_compliance_report = AsyncMock(
        return_value={
            "review_id": rid,
            "review_type": "structural",
            "status": "completed",
            "standards_checked": ["ISO 19901"],
            "passed_count": 10,
            "failed_count": 2,
            "violations": [{"clause": "4.2.1", "message": "不足"}],
            "suggestions": [{"issue": "weak_point", "severity": "high", "suggestion": "補強必要"}],
        }
    )

    response = client.get(
        f"/api/v1/advanced/design-reviews/{rid}/compliance-report",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "completed"
    assert data["data"]["passed_count"] == 10
    assert data["data"]["failed_count"] == 2


# ============================================
# 13. Predictive Model CRUD
# ============================================
def test_create_predictive_model(client, auth_headers):
    mock_model = _make_mock_predictive()

    import src.api.predictive as pred_module
    pred_module.create_predictive_model = AsyncMock(return_value=mock_model)

    response = client.post(
        "/api/v1/advanced/predictive",
        json={
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "asset_name": "Excavator Unit 5",
            "asset_type": "heavy_machinery",
            "model_type": "remaining_useful_life",
            "failure_probability": 0.15,
            "remaining_life_days": 180,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["asset_name"] == "Excavator Unit 5"


# ============================================
# 14. Prediction Result
# ============================================
def test_get_prediction_result(client, auth_headers):
    pid = uuid4()
    from datetime import date

    import src.api.predictive as pred_module
    pred_module.get_prediction_result = AsyncMock(
        return_value={
            "model_id": pid,
            "asset_name": "Excavator Unit 5",
            "asset_type": "heavy_machinery",
            "model_type": "remaining_useful_life",
            "status": "active",
            "failure_probability": 0.15,
            "remaining_life_days": 180,
            "next_maintenance_predicted": date(2026, 6, 15),
            "recommendations": [{"action": "replace_hydraulic_seal", "priority": "high"}],
        }
    )

    response = client.get(
        f"/api/v1/advanced/predictive/{pid}/prediction",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["failure_probability"] == 0.15
    assert data["data"]["remaining_life_days"] == 180


# ============================================
# 15. Marine List (filtered)
# ============================================
def test_list_marine_constructions(client, auth_headers):
    mock_marine = _make_mock_marine()

    import src.api.marine as marine_module
    marine_module.list_marine_constructions = AsyncMock(
        return_value=([mock_marine], 1)
    )

    response = client.get(
        "/api/v1/advanced/marine",
        params={"organization_id": "00000000-0000-0000-0000-000000000001", "page": 1, "per_page": 20},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["meta"]["total"] == 1


# ============================================
# 16. Schema Validation - Marine Create Missing Required
# ============================================
def test_marine_create_invalid_request(client, auth_headers):
    response = client.post(
        "/api/v1/advanced/marine",
        json={"name": "Test"},
        headers=auth_headers,
    )
    assert response.status_code == 422
