"""内部API (canonical/work-area 保存) テスト"""

import io
from datetime import datetime, timezone

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.config import get_settings
from src.main import create_app
from src.models import Document
from src.models.base import get_db
from src.services import storage_service


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
        tags=[],
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


@pytest.fixture
def storage(tmp_path, monkeypatch):
    """実体ファイル転送をローカルFSへ向ける(実ファイルを検証するため)。"""
    root = tmp_path / "canonical"
    get_settings.cache_clear()
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")
    monkeypatch.setenv("CANONICAL_STORAGE_ROOT", str(root))
    monkeypatch.delenv("ONEDRIVE_ENABLED", raising=False)
    monkeypatch.setattr(
        storage_service, "get_file_stream", lambda key: io.BytesIO(b"hello world")
    )
    yield root
    get_settings.cache_clear()


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
    def test_store_canonical_success(self, app, internal_api_key, storage):
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
        body = response.json()
        assert body["success"] is True
        assert document.canonical_stored_at is not None
        assert document.canonical_storage_backend == "filesystem"
        assert body["data"]["stored"] is True

        # 実体ファイルが本当に保存されていること
        stored_file = storage / document.canonical_path
        assert stored_file.exists()
        assert stored_file.read_bytes() == b"hello world"
        assert document.canonical_storage_error is None
        mock_db.flush.assert_awaited()

    def test_store_work_area_success(self, app, internal_api_key, storage):
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

        stored_file = storage / document.work_area_path
        assert stored_file.exists()
        assert stored_file.read_bytes() == b"hello world"
        assert "work-areas/R-2026-0001" in document.work_area_path
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


class TestInternalStorageFailure:
    """保存できない場合は成功を返さず、失敗をDBへ記録して 5xx を返す。"""

    def test_not_configured_returns_503_and_records_error(
        self, app, internal_api_key, monkeypatch
    ):
        get_settings.cache_clear()
        monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")
        monkeypatch.delenv("CANONICAL_STORAGE_ROOT", raising=False)
        monkeypatch.delenv("ONEDRIVE_ENABLED", raising=False)

        document = _make_document(uuid4())
        client, mock_db = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
        )
        get_settings.cache_clear()

        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "STORAGE_NOT_CONFIGURED"
        # 「保存した」と記録していないこと
        assert document.canonical_stored_at is None
        assert document.canonical_storage_error is not None
        # 失敗記録がロールバックされないよう明示的にコミットしていること
        mock_db.commit.assert_awaited()

    def test_missing_source_object_returns_502(self, app, internal_api_key, storage,
                                              monkeypatch):
        monkeypatch.setattr(storage_service, "get_file_stream", lambda key: None)
        document = _make_document(uuid4())
        client, mock_db = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-work-area",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
            data={"receipt_no": "R-2026-0002"},
        )

        assert response.status_code == 502
        assert response.json()["detail"]["code"] == "SOURCE_FILE_NOT_FOUND"
        assert document.work_area_stored_at is None
        assert document.work_area_storage_error is not None
        # 作業領域の失敗が正本の記録を汚さないこと(操作別カラム)
        assert document.canonical_storage_error is None
        mock_db.commit.assert_awaited()

    def test_work_area_success_does_not_clear_canonical_failure(
        self, app, internal_api_key, storage, monkeypatch
    ):
        """正本保存の失敗記録が、後続の作業領域保存の成功で消えないこと。"""
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)
        headers = {
            "X-Internal-API-Key": internal_api_key,
            "X-Organization-ID": str(document.organization_id),
        }

        monkeypatch.setattr(storage_service, "get_file_stream", lambda key: None)
        first = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical",
            headers=headers,
        )
        assert first.status_code == 502
        assert document.canonical_storage_error is not None

        monkeypatch.setattr(
            storage_service, "get_file_stream", lambda key: io.BytesIO(b"hello world")
        )
        second = client.post(
            f"/api/v1/documents/internal/{document.id}/store-work-area",
            headers=headers,
            data={"receipt_no": "R-2026-0003"},
        )
        assert second.status_code == 200

        assert document.canonical_storage_error is not None
        assert document.work_area_storage_error is None
        assert document.work_area_storage_backend == "filesystem"

    def test_receipt_number_cannot_escape_storage_root(self, app, internal_api_key, storage):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)

        response = client.post(
            f"/api/v1/documents/internal/{document.id}/store-work-area",
            headers={
                "X-Internal-API-Key": internal_api_key,
                "X-Organization-ID": str(document.organization_id),
            },
            data={"receipt_no": ".." + "/" + ".." + "/" + "escaped"},
        )
        assert response.status_code == 200
        target = (storage / document.work_area_path).resolve()
        assert storage.resolve() in target.parents
        assert target.exists()



class TestStorageStatusIsObservable:
    """保存状態が API レスポンスから確認できること(DB を見ないと分からない状態を避ける)。"""

    def test_detail_response_exposes_storage_status(self, app, internal_api_key, storage):
        document = _make_document(uuid4())
        client, _ = _client_with_document(app, document)
        headers = {
            "X-Internal-API-Key": internal_api_key,
            "X-Organization-ID": str(document.organization_id),
        }

        stored = client.post(
            f"/api/v1/documents/internal/{document.id}/store-canonical", headers=headers
        )
        assert stored.status_code == 200

        from src.schemas import DocumentResponse

        payload = DocumentResponse.model_validate(document).model_dump()
        assert payload["canonical_stored_at"] is not None
        assert payload["canonical_storage_backend"] == "filesystem"
        assert payload["canonical_path"] == document.canonical_path
        assert payload["canonical_storage_error"] is None
        assert payload["work_area_stored_at"] is None
