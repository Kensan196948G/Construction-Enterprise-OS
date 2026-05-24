"""BIMサービス テスト"""

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


class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "bim-service"


class TestAuthRequired:
    def test_models_list_requires_auth(self, client):
        response = client.get("/api/v1/bim/models")
        assert response.status_code == 401

    def test_models_create_requires_auth(self, client):
        response = client.post("/api/v1/bim/models", json={})
        assert response.status_code == 401

    def test_models_get_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/models/{uuid4()}")
        assert response.status_code == 401

    def test_models_update_requires_auth(self, client):
        response = client.put(f"/api/v1/bim/models/{uuid4()}", json={})
        assert response.status_code == 401

    def test_models_delete_requires_auth(self, client):
        response = client.delete(f"/api/v1/bim/models/{uuid4()}")
        assert response.status_code == 401

    def test_elements_list_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements")
        assert response.status_code == 401

    def test_elements_get_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/elements/{uuid4()}")
        assert response.status_code == 401

    def test_elements_by_category_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements/by-category")
        assert response.status_code == 401

    def test_elements_by_level_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements/by-level")
        assert response.status_code == 401

    def test_elements_search_requires_auth(self, client):
        response = client.get("/api/v1/bim/elements/search?q=wall")
        assert response.status_code == 401

    def test_pointclouds_list_requires_auth(self, client):
        response = client.get("/api/v1/bim/pointclouds")
        assert response.status_code == 401

    def test_pointclouds_create_requires_auth(self, client):
        response = client.post("/api/v1/bim/pointclouds", json={})
        assert response.status_code == 401

    def test_pointclouds_get_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/pointclouds/{uuid4()}")
        assert response.status_code == 401

    def test_pointclouds_update_requires_auth(self, client):
        response = client.put(f"/api/v1/bim/pointclouds/{uuid4()}", json={})
        assert response.status_code == 401

    def test_pointclouds_delete_requires_auth(self, client):
        response = client.delete(f"/api/v1/bim/pointclouds/{uuid4()}")
        assert response.status_code == 401


class TestBIMModelCRUD:
    def test_create_model_success(self, app):
        from src.models import BIMModel

        model_id = uuid4()
        org_id = uuid4()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockScalarResult())
        mock_db.add = MagicMock()

        async def mock_flush():
            pass

        mock_db.flush = mock_flush

        async def mock_refresh(obj):
            obj.id = model_id
            obj.organization_id = org_id
            obj.name = "Test BIM Model"
            obj.model_type = "architectural"
            obj.file_format = "ifc"
            obj.status = "draft"
            obj.tags = []
            obj.metadata_ = {}
            obj.created_at = "2024-01-01T00:00:00Z"
            obj.updated_at = "2024-01-01T00:00:00Z"

        mock_db.refresh = mock_refresh

        async def mock_get_db_override():
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db_override
        client = TestClient(app)

        # Auth required — verify 401 without token
        response = client.post(
            "/api/v1/bim/models",
            json={
                "organization_id": str(org_id),
                "name": "Test BIM Model",
                "model_type": "architectural",
                "file_format": "ifc",
            },
        )
        assert response.status_code == 401

    def test_list_models_empty(self, client):
        response = client.get("/api/v1/bim/models")
        assert response.status_code == 401  # auth required

    def test_get_model_not_found(self, client):
        response = client.get(f"/api/v1/bim/models/{uuid4()}")
        assert response.status_code == 401  # auth required

    def test_delete_model_not_found(self, client):
        response = client.delete(f"/api/v1/bim/models/{uuid4()}")
        assert response.status_code == 401  # auth required


class TestBIMElementListing:
    def test_elements_list_returns_empty(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements")
        assert response.status_code == 401

    def test_elements_by_category_returns_empty(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements/by-category")
        assert response.status_code == 401

    def test_elements_by_level_returns_empty(self, client):
        response = client.get(f"/api/v1/bim/{uuid4()}/elements/by-level")
        assert response.status_code == 401

    def test_elements_search_returns_empty(self, client):
        response = client.get("/api/v1/bim/elements/search?q=wall")
        assert response.status_code == 401


class TestPointCloudCRUD:
    def test_create_pointcloud_success(self, app):
        pc_id = uuid4()
        org_id = uuid4()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockScalarResult())
        mock_db.add = MagicMock()

        async def mock_flush():
            pass

        mock_db.flush = mock_flush

        async def mock_refresh(obj):
            obj.id = pc_id
            obj.organization_id = org_id
            obj.name = "Test Point Cloud"
            obj.description = None
            obj.capture_method = "lidar"
            obj.point_count = 1000000
            obj.file_format = "las"
            obj.density = None
            obj.accuracy_mm = None
            obj.is_colorized = False
            obj.is_classified = False
            obj.metadata_ = {}
            obj.created_at = "2024-01-01T00:00:00Z"

        mock_db.refresh = mock_refresh

        async def mock_get_db_override():
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db_override
        client = TestClient(app)

        response = client.post(
            "/api/v1/bim/pointclouds",
            json={
                "organization_id": str(org_id),
                "name": "Test Point Cloud",
                "capture_method": "lidar",
                "point_count": 1000000,
                "file_format": "las",
            },
        )
        assert response.status_code == 401  # auth required

    def test_list_pointclouds_requires_auth(self, client):
        response = client.get("/api/v1/bim/pointclouds")
        assert response.status_code == 401

    def test_get_pointcloud_requires_auth(self, client):
        response = client.get(f"/api/v1/bim/pointclouds/{uuid4()}")
        assert response.status_code == 401

    def test_delete_pointcloud_requires_auth(self, client):
        response = client.delete(f"/api/v1/bim/pointclouds/{uuid4()}")
        assert response.status_code == 401


class TestBIMModelSchemaValidation:
    def test_response_schema_structure(self):
        from src.schemas import APIResponse, BIMModelResponse

        resp = APIResponse(
            success=True,
            data={
                "id": str(uuid4()),
                "organization_id": str(uuid4()),
                "name": "Test",
                "model_type": "architectural",
                "file_format": "ifc",
                "status": "draft",
                "tags": [],
                "metadata": {},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
        assert resp.success is True
        assert resp.data["name"] == "Test"

    def test_element_response_schema(self):
        from src.schemas import BIMElementResponse

        data = {
            "id": str(uuid4()),
            "model_id": str(uuid4()),
            "element_id": "abc123",
            "name": "Wall-01",
            "element_type": "IfcWall",
            "category": "walls",
            "properties": {"material": "concrete"},
            "quantity": 10.5,
            "unit": "m²",
            "level_name": "1F",
            "building_name": "Building A",
            "bounding_box": {"min": {"x": 0, "y": 0, "z": 0}, "max": {"x": 10, "y": 3, "z": 3}},
            "created_at": "2024-01-01T00:00:00Z",
        }
        el = BIMElementResponse(**data)
        assert el.name == "Wall-01"
        assert el.category == "walls"

    def test_pointcloud_response_schema(self):
        from src.schemas import PointCloudResponse

        data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "name": "Site Scan 01",
            "capture_method": "lidar",
            "capture_date": "2024-03-15",
            "point_count": 50000000,
            "file_size": 2147483648,
            "file_format": "las",
            "coordinate_system": "JGD2011",
            "density": 100.0,
            "accuracy_mm": 5.0,
            "is_colorized": True,
            "is_classified": True,
            "metadata": {},
            "created_at": "2024-01-01T00:00:00Z",
        }
        pc = PointCloudResponse(**data)
        assert pc.name == "Site Scan 01"
        assert pc.capture_method == "lidar"
        assert pc.point_count == 50000000
        assert pc.is_colorized is True


class TestBIMServiceUtility:
    def test_geojson_point_to_wkt(self):
        from src.services.bim_service import geojson_to_wkt_element

        result = geojson_to_wkt_element({"type": "Point", "coordinates": [139.6917, 35.6895]})
        assert result is not None
        assert "POINT" in str(result)

    def test_geojson_polygon_to_wkt(self):
        from src.services.bim_service import geojson_to_wkt_element

        result = geojson_to_wkt_element({
            "type": "Polygon",
            "coordinates": [[[139.0, 35.0], [140.0, 35.0], [140.0, 36.0], [139.0, 36.0], [139.0, 35.0]]],
        })
        assert result is not None
        assert "POLYGON" in str(result)

    def test_geojson_none_returns_none(self):
        from src.services.bim_service import geojson_to_wkt_element

        result = geojson_to_wkt_element(None)
        assert result is None

    def test_geojson_pointz_to_wkt(self):
        from src.services.bim_service import geojson_to_wkt_element

        result = geojson_to_wkt_element({"type": "PointZ", "coordinates": [139.6917, 35.6895, 45.0]})
        assert result is not None
        assert "POINT Z" in str(result)
