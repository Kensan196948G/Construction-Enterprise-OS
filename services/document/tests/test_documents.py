"""文書管理サービス テスト"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
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


def _auth_headers(user_id: str | None = None, org_id: str | None = None) -> dict:
    from jose import jwt

    from src.config import get_settings

    settings = get_settings()
    payload = {
        "sub": user_id or str(uuid4()),
        "type": "user",
        "org": org_id or str(uuid4()),
        "roles": ["admin"],
        "scopes": ["documents:read", "documents:write"],
    }
    token = jwt.encode(
        payload, settings.jwt_public_key, algorithm=settings.JWT_ALGORITHM
    )
    return {"Authorization": f"Bearer {token}"}


class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "document-service"


class TestAuthRequired:
    endpoints = [
        ("GET", "/api/v1/documents"),
        ("GET", f"/api/v1/documents/{uuid4()}"),
        ("GET", f"/api/v1/documents/{uuid4()}/download"),
        ("GET", f"/api/v1/documents/{uuid4()}/versions"),
        ("GET", f"/api/v1/documents/{uuid4()}/versions/1"),
    ]

    def test_all_endpoints_require_auth(self, client):
        for method, url in self.endpoints:
            response = client.request(method, url)
            assert (
                response.status_code == 401
            ), f"{method} {url} returned {response.status_code}"

    def test_upload_requires_auth(self, client):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", b"test content", "application/pdf")},
        )
        assert response.status_code == 401

    def test_put_requires_auth(self, client):
        response = client.put(f"/api/v1/documents/{uuid4()}", json={"name": "Updated"})
        assert response.status_code == 401

    def test_delete_requires_auth(self, client):
        response = client.delete(f"/api/v1/documents/{uuid4()}")
        assert response.status_code == 401

    def test_version_upload_requires_auth(self, client):
        response = client.post(
            f"/api/v1/documents/{uuid4()}/versions",
            files={"file": ("test.pdf", b"test content", "application/pdf")},
        )
        assert response.status_code == 401


class TestStorageKeyGeneration:
    def test_generate_storage_key(self):
        from src.services.storage_service import generate_storage_key

        org_id = uuid4()
        doc_id = uuid4()
        key = generate_storage_key(org_id, doc_id, 3, "drawing.pdf")

        assert str(org_id) in key
        assert str(doc_id) in key
        assert "v3" in key
        assert "drawing.pdf" in key

    def test_generate_storage_key_format(self):
        from src.services.storage_service import generate_storage_key

        org_id = uuid4()
        doc_id = uuid4()
        key = generate_storage_key(org_id, doc_id, 1, "file.txt")
        expected = f"{org_id}/{doc_id}/v1/file.txt"
        assert key == expected


class TestDocumentService:
    @pytest.mark.asyncio
    async def test_create_document(self, app):
        from unittest.mock import AsyncMock, MagicMock
        from uuid import uuid4

        from src.services.document_service import create_document

        doc_id = uuid4()
        org_id = uuid4()
        user_id = uuid4()

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        async def mock_refresh(obj):
            obj.id = doc_id
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh = mock_refresh

        with patch("src.services.document_service.upload_file", return_value=True):
            document = await create_document(
                mock_db,
                organization_id=org_id,
                created_by=user_id,
                name="Test Document",
                file_name="test.pdf",
                file_content=b"content",
                content_type="application/pdf",
                document_type="pdf",
            )

        assert document is not None
        assert mock_db.add.call_count == 2

    @pytest.mark.asyncio
    async def test_soft_delete_document(self, app):
        from unittest.mock import AsyncMock, MagicMock
        from uuid import uuid4
        from datetime import datetime, timezone

        from src.models import Document
        from src.services.document_service import soft_delete_document

        doc_id = uuid4()
        mock_db = AsyncMock()

        mock_result = MagicMock()
        doc = Document(
            id=doc_id,
            organization_id=uuid4(),
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
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result

        async def mock_refresh(obj):
            pass

        mock_db.refresh = mock_refresh

        result = await soft_delete_document(mock_db, doc_id)
        assert result is not None
        assert result.status == "deleted"

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent(self, app):
        from unittest.mock import AsyncMock, MagicMock
        from uuid import uuid4

        from src.services.document_service import soft_delete_document

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await soft_delete_document(mock_db, uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_create_new_version(self, app):
        from unittest.mock import AsyncMock, MagicMock, patch
        from uuid import uuid4
        from datetime import datetime, timezone

        from src.models import Document, DocumentVersion
        from src.services.document_service import create_new_version

        doc_id = uuid4()
        org_id = uuid4()
        user_id = uuid4()

        mock_db = AsyncMock()
        mock_db.add = MagicMock()

        doc = Document(
            id=doc_id,
            organization_id=org_id,
            name="Original",
            document_type="pdf",
            status="draft",
            current_version=1,
            file_name="original.pdf",
            file_size=100,
            mime_type="application/pdf",
            storage_key=f"{org_id}/{doc_id}/v1/original.pdf",
            created_by=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result

        async def mock_refresh(obj):
            if isinstance(obj, DocumentVersion):
                obj.id = uuid4()
                obj.created_at = datetime.now(timezone.utc)

        mock_db.refresh = mock_refresh

        with patch("src.services.document_service.upload_file", return_value=True):
            version = await create_new_version(
                mock_db,
                document_id=doc_id,
                created_by=user_id,
                file_content=b"new content",
                file_name="updated.pdf",
                content_type="application/pdf",
                change_description="Updated fields",
            )

        assert version is not None
        assert doc.current_version == 2
        assert mock_db.add.call_count == 1
