"""Platformサービス テスト"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db


class MockScalarResult:
    def scalar_one_or_none(self):
        return None

    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None


@pytest.fixture
def app():
    _app = create_app()
    mock_db = AsyncMock()

    async def mock_execute(*args, **kwargs):
        return MockScalarResult()

    mock_db.execute = mock_execute
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()

    async def mock_get_db():
        yield mock_db

    _app.dependency_overrides[get_db] = mock_get_db
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


# ============================================
# Test 1: Health Check
# ============================================
class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "platform-service"


# ============================================
# Test 2-5: Auth Required
# ============================================
class TestAuthRequired:
    def test_viewer_configs_list_requires_auth(self, client):
        response = client.get("/platform/viewer/configs")
        assert response.status_code == 401

    def test_viewer_configs_create_requires_auth(self, client):
        response = client.post("/platform/viewer/configs", json={})
        assert response.status_code == 401

    def test_iot_dashboards_list_requires_auth(self, client):
        response = client.get("/platform/iot/dashboards")
        assert response.status_code == 401

    def test_iot_device_groups_list_requires_auth(self, client):
        response = client.get("/platform/iot/device-groups")
        assert response.status_code == 401


# ============================================
# Test 6-8: Viewer Config CRUD
# ============================================
class TestViewerConfigCRUD:
    def test_create_viewer_config_requires_auth(self, client):
        org_id = uuid4()
        response = client.post(
            "/platform/viewer/configs",
            json={
                "organization_id": str(org_id),
                "name": "Test Viewer",
                "viewer_type": "bim_3d",
            },
        )
        assert response.status_code == 401

    def test_get_viewer_config_requires_auth(self, client):
        response = client.get(f"/platform/viewer/configs/{uuid4()}")
        assert response.status_code == 401

    def test_delete_viewer_config_requires_auth(self, client):
        response = client.delete(f"/platform/viewer/configs/{uuid4()}")
        assert response.status_code == 401


# ============================================
# Test 9: Scene Management
# ============================================
class TestSceneManagement:
    def test_create_scene_requires_auth(self, client):
        config_id = uuid4()
        response = client.post(
            f"/platform/viewer/configs/{config_id}/scenes",
            json={
                "name": "Scene 1",
                "camera_state": {"position": {"x": 0, "y": 0, "z": 10}, "target": {"x": 0, "y": 0, "z": 0}},
            },
        )
        assert response.status_code == 401

    def test_get_scene_requires_auth(self, client):
        response = client.get(f"/platform/viewer/scenes/{uuid4()}")
        assert response.status_code == 401


# ============================================
# Test 10-12: Dashboard CRUD
# ============================================
class TestDashboardCRUD:
    def test_create_dashboard_requires_auth(self, client):
        org_id = uuid4()
        response = client.post(
            "/platform/iot/dashboards",
            json={
                "organization_id": str(org_id),
                "name": "Test Dashboard",
                "layout": {"widgets": []},
            },
        )
        assert response.status_code == 401

    def test_update_dashboard_requires_auth(self, client):
        response = client.put(
            f"/platform/iot/dashboards/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 401


# ============================================
# Test 13-15: Device Group CRUD
# ============================================
class TestDeviceGroupCRUD:
    def test_create_device_group_requires_auth(self, client):
        org_id = uuid4()
        response = client.post(
            "/platform/iot/device-groups",
            json={
                "organization_id": str(org_id),
                "name": "Site Sensors",
                "group_type": "site",
            },
        )
        assert response.status_code == 401

    def test_update_device_group_devices_requires_auth(self, client):
        group_id = uuid4()
        response = client.put(
            f"/platform/iot/device-groups/{group_id}/devices",
            json={"device_ids": [str(uuid4())]},
        )
        assert response.status_code == 401

    def test_get_device_group_requires_auth(self, client):
        response = client.get(f"/platform/iot/device-groups/{uuid4()}")
        assert response.status_code == 401


# ============================================
# Test 16: Schema Validation
# ============================================
class TestSchemaValidation:
    def test_viewer_config_response_schema(self):
        from src.schemas import APIResponse

        resp = APIResponse(
            success=True,
            data={
                "id": str(uuid4()),
                "organization_id": str(uuid4()),
                "name": "Test Viewer",
                "viewer_type": "bim_3d",
                "model_ids": [],
                "layer_ids": [],
                "camera_state": {},
                "visible_categories": [],
                "clipping_planes": {},
                "theme": "light",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
        assert resp.success is True
        assert resp.data["name"] == "Test Viewer"
        assert resp.data["viewer_type"] == "bim_3d"

    def test_dashboard_response_schema(self):
        from src.schemas import IoTDashboardResponse

        data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "name": "Factory Dashboard",
            "description": "工場モニタリング",
            "layout": {"widgets": [{"type": "gauge", "config": {"deviceId": str(uuid4())}}]},
            "refresh_interval_seconds": 10,
            "is_public": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        db = IoTDashboardResponse(**data)
        assert db.name == "Factory Dashboard"
        assert db.layout["widgets"][0]["type"] == "gauge"
        assert db.refresh_interval_seconds == 10

    def test_device_group_response_schema(self):
        from src.schemas import DeviceGroupResponse

        data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "name": "Site A Sensors",
            "description": None,
            "device_ids": [str(uuid4()), str(uuid4())],
            "group_type": "site",
            "parent_group_id": None,
            "created_at": "2024-01-01T00:00:00Z",
        }
        group = DeviceGroupResponse(**data)
        assert group.name == "Site A Sensors"
        assert len(group.device_ids) == 2
        assert group.group_type == "site"

    def test_viewer_scene_response_schema(self):
        from src.schemas import ViewerSceneResponse

        data = {
            "id": str(uuid4()),
            "config_id": str(uuid4()),
            "name": "Front View",
            "description": "正面からの視点",
            "camera_state": {"position": {"x": 0, "y": 10, "z": 5}, "target": {"x": 0, "y": 0, "z": 0}},
            "annotations": [{"position": {"x": 1, "y": 2, "z": 3}, "text": "注釈", "color": "#ff0000"}],
            "measurements": [],
            "created_at": "2024-01-01T00:00:00Z",
        }
        scene = ViewerSceneResponse(**data)
        assert scene.name == "Front View"
        assert len(scene.annotations) == 1
        assert scene.annotations[0]["text"] == "注釈"


# ============================================
# Test 17: Service Utility
# ============================================
class TestPlatformService:
    def test_validate_widget_type_valid(self):
        from src.services.platform_service import validate_widget_type

        assert validate_widget_type("gauge") is True
        assert validate_widget_type("chart") is True
        assert validate_widget_type("map") is True
        assert validate_widget_type("table") is True

    def test_validate_widget_type_invalid(self):
        from src.services.platform_service import validate_widget_type

        assert validate_widget_type("invalid_type") is False

    def test_normalize_interval_seconds(self):
        from src.services.platform_service import normalize_interval_seconds

        assert normalize_interval_seconds(10) == 10
        assert normalize_interval_seconds(0) == 1
        assert normalize_interval_seconds(-5) == 1
        assert normalize_interval_seconds(5000) == 3600
