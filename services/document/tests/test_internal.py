"""内部API (canonical/work-area 保存) テスト"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import create_app
from src.models import Document
from src.models.base import get_db


def _make_document(org_id) -> Document:
    return Document(
        id=uuid4(),
        organization_id=org_id,
        name="Test",
        document_type="pdf",
        status="draft",
        current_version=1,
        file_name="test.pdf",
        file_size=100,
        mime_type="application/pdf",
        storage_key="key",
        created_by=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def internal_api_key(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")
    yield "test-internal-key"
    get_settings.cache_clear()


@pytest.fixture
def app(internal_api_key):
    _app = create_app()
    return _app


def _client_with_document(app, document):
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = document
    mock_db.execute.return_value = mock_result
    mock_db.flush = AsyncMock()

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    return TestClient(app), mock_db


class TestInternalAuth:
    def test_store_canonical_missing_key_rejected(self, app):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)
        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers={"X-Organization-ID": str(document.organization_id)},
        )
        assert response.status_code == 403

    def test_store_canonical_wrong_key_rejected(self, app):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)
        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers={
                "X-Internal-API-Key": "wrong-key",
                "X-Organization-ID": str(document.organization_id),
            },
        )
        assert response.status_code == 403


class TestInternalOrganizationCheck:
    def test_store_canonical_organization_mismatch_forbidden(
        self, app, internal_api_key
    ):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)
        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(uuid4()),
            },
        )
        assert response.status_code == 403


class TestInternalNotFound:
    def test_store_canonical_document_not_found(self, app, internal_api_key):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        async def mock_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db
        client = TestClient(app)

        response = client.post(
            f"/api/v1/documents/internal/{uuid4()}/store-canonical",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(uuid4()),
            },
        )
        assert response.status_code == 404


class TestInternalSuccess:
    def test_store_canonical_success(self, app, internal_api_key):
        document = _make_document(uuid4())
        client, mock_db = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert document.canonical_stored_at is not None
        mock_db.flush.assert_awaited()

    def test_store_work_area_success(self, app, internal_api_key):
        document = _make_document(uuid4())
        client, mock_db = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-work-area",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
            data={"receipt_no": "R-2026-0001"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert document.work_area_receipt_no == "R-2026-0001"
        assert document.work_area_stored_at is not None
        mock_db.flush.assert_awaited()

    def test_store_work_area_requires_receipt_no(self, app, internal_api_key):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-work-area",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
        )
        assert response.status_code == 422
