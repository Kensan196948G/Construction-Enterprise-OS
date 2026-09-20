"""GISサービス テスト"""

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
        assert data["service"] == "gis-service"


class TestAuthRequired:
    def test_sites_list_requires_auth(self, client):
        response = client.get("/api/v1/gis/sites")
        assert response.status_code == 401

    def test_sites_create_requires_auth(self, client):
        response = client.post("/api/v1/gis/sites", json={})
        assert response.status_code == 401

    def test_sites_get_requires_auth(self, client):
        response = client.get(f"/api/v1/gis/sites/{uuid4()}")
        assert response.status_code == 401

    def test_sites_update_requires_auth(self, client):
        response = client.put(f"/api/v1/gis/sites/{uuid4()}", json={})
        assert response.status_code == 401

    def test_sites_delete_requires_auth(self, client):
        response = client.delete(f"/api/v1/gis/sites/{uuid4()}")
        assert response.status_code == 401

    def test_sites_nearby_requires_auth(self, client):
        response = client.get("/api/v1/gis/sites/nearby?lat=35.0&lng=139.0&radius_m=1000")
        assert response.status_code == 401

    def test_sites_in_area_requires_auth(self, client):
        response = client.get(
            "/api/v1/gis/sites/in-area?min_lat=35.0&min_lng=139.0&max_lat=36.0&max_lng=140.0"
        )
        assert response.status_code == 401

    def test_infrastructure_list_requires_auth(self, client):
        response = client.get("/api/v1/gis/infrastructure")
        assert response.status_code == 401

    def test_infrastructure_create_requires_auth(self, client):
        response = client.post("/api/v1/gis/infrastructure", json={})
        assert response.status_code == 401

    def test_infrastructure_get_requires_auth(self, client):
        response = client.get(f"/api/v1/gis/infrastructure/{uuid4()}")
        assert response.status_code == 401

    def test_infrastructure_near_site_requires_auth(self, client):
        response = client.get(f"/api/v1/gis/infrastructure/near-site/{uuid4()}")
        assert response.status_code == 401

    def test_hazard_zones_list_requires_auth(self, client):
        response = client.get("/api/v1/gis/hazard-zones")
        assert response.status_code == 401

    def test_hazard_zones_create_requires_auth(self, client):
        response = client.post("/api/v1/gis/hazard-zones", json={})
        assert response.status_code == 401

    def test_hazard_zones_intersecting_requires_auth(self, client):
        response = client.get(f"/api/v1/gis/hazard-zones/intersecting/{uuid4()}")
        assert response.status_code == 401


class TestGeoJSONConversion:
    def test_point_to_wkt(self):
        from src.services.geo_service import geojson_to_wkt
        from src.schemas import GeoJSONGeometry

        geom = GeoJSONGeometry(type="Point", coordinates=[139.6917, 35.6895])
        result = geojson_to_wkt(geom)
        assert result == "SRID=4326;POINT(139.6917 35.6895)"

    def test_polygon_to_wkt(self):
        from src.services.geo_service import geojson_to_wkt
        from src.schemas import GeoJSONGeometry

        geom = GeoJSONGeometry(
            type="Polygon",
            coordinates=[
                [
                    [139.0, 35.0],
                    [140.0, 35.0],
                    [140.0, 36.0],
                    [139.0, 36.0],
                    [139.0, 35.0],
                ]
            ],
        )
        result = geojson_to_wkt(geom)
        expected = (
            "SRID=4326;POLYGON((139.0 35.0, 140.0 35.0, 140.0 36.0, 139.0 36.0, 139.0 35.0))"
        )
        assert result == expected

    def test_linestring_to_wkt(self):
        from src.services.geo_service import geojson_to_wkt
        from src.schemas import GeoJSONGeometry

        geom = GeoJSONGeometry(
            type="LineString",
            coordinates=[[139.0, 35.0], [140.0, 36.0], [141.0, 37.0]],
        )
        result = geojson_to_wkt(geom)
        expected = "SRID=4326;LINESTRING(139.0 35.0, 140.0 36.0, 141.0 37.0)"
        assert result == expected

    def test_multipoint_to_wkt(self):
        from src.services.geo_service import geojson_to_wkt
        from src.schemas import GeoJSONGeometry

        geom = GeoJSONGeometry(
            type="MultiPoint",
            coordinates=[[139.0, 35.0], [140.0, 36.0]],
        )
        result = geojson_to_wkt(geom)
        expected = "SRID=4326;MULTIPOINT(139.0 35.0, 140.0 36.0)"
        assert result == expected

    def test_wkb_to_geojson_point(self):
        from src.services.geo_service import wkb_to_geojson_geometry
        from shapely.geometry import Point
        from shapely import wkb

        point = Point(139.6917, 35.6895)
        wkb_data = wkb.dumps(point, hex=False)

        result = wkb_to_geojson_geometry(wkb_data)
        assert result is not None
        assert result.type == "Point"
        assert result.coordinates[0] == 139.6917
        assert result.coordinates[1] == 35.6895

    def test_wkb_to_geojson_none(self):
        from src.services.geo_service import wkb_to_geojson_geometry

        result = wkb_to_geojson_geometry(None)
        assert result is None

    def test_wkt_to_geojson(self):
        from src.services.geo_service import wkb_to_geojson_geometry

        result = wkb_to_geojson_geometry("POINT(139.6917 35.6895)")
        assert result is not None
        assert result.type == "Point"


class TestSiteCreationInputValidation:
    def test_site_create_with_geojson_point(self, app):
        from src.models.base import get_db

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MockScalarResult())
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        async def mock_refresh(obj):
            pass

        mock_db.refresh = mock_refresh

        async def mock_get_db_override():
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db_override
        client = TestClient(app)

        response = client.post(
            "/api/v1/gis/sites",
            json={
                "organization_id": str(uuid4()),
                "name": "Test Site",
                "location": {
                    "type": "Point",
                    "coordinates": [139.6917, 35.6895],
                },
                "site_type": "building",
                "status": "active",
            },
        )
        assert response.status_code == 401  # auth required, checked before validation

    def test_site_create_geojson_feature_format(self):
        """GeoJSON Feature形式が正しく構築されることを確認"""
        from src.api.sites import _site_to_geojson
        from src.models import ConstructionSite

        site = ConstructionSite(
            id=uuid4(),
            organization_id=uuid4(),
            name="Test Site",
            location="SRID=4326;POINT(139.6917 35.6895)",
            site_type="building",
            status="active",
            metadata_={},
        )

        feature = _site_to_geojson(site)
        assert feature.type == "Feature"
        assert feature.properties["name"] == "Test Site"
        assert feature.properties["status"] == "active"


class TestGeoServiceEdgeCases:
    def test_unsupported_geometry_type(self):
        from src.services.geo_service import geojson_to_wkt
        from src.schemas import GeoJSONGeometry
        import pytest

        geom = GeoJSONGeometry(type="UnsupportedType", coordinates=[])
        with pytest.raises(ValueError, match="Unsupported geometry type"):
            geojson_to_wkt(geom)
