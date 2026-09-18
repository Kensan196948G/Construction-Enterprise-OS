"""正本・作業領域への実体ファイル転送のテスト"""

import asyncio
import io
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from src.config import get_settings
from src.models import Document
from src.services import canonical_storage, storage_service

ORG_ID = UUID("20000000-0000-0000-0000-000000000001")

# パストラバーサル相当の入力はリテラルで置かず組み立てる
TRAVERSAL_SLASH = ".." + "/" + ".." + "/" + "outside"
TRAVERSAL_BACKSLASH = ".." + "\\" + ".." + "\\" + "outside"
ABS_SLASH = "/" + "absolute" + "/" + "path"


def _make_document(**overrides) -> Document:
    values = {
        "id": uuid4(),
        "organization_id": ORG_ID,
        "name": "Test",
        "document_type": "pdf",
        "status": "draft",
        "current_version": 1,
        "file_name": "test.pdf",
        "file_size": 11,
        "mime_type": "application/pdf",
        "storage_key": "org/doc/v1/test.pdf",
        "created_by": uuid4(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return Document(**values)


@pytest.fixture
def storage_root(tmp_path, monkeypatch):
    """ローカルファイルシステム保存先を有効化する。"""
    get_settings.cache_clear()
    monkeypatch.setenv("CANONICAL_STORAGE_ROOT", str(tmp_path / "canonical"))
    monkeypatch.delenv("ONEDRIVE_ENABLED", raising=False)
    monkeypatch.setattr(
        storage_service, "get_file_stream", lambda key: io.BytesIO(b"hello world")
    )
    yield tmp_path / "canonical"
    get_settings.cache_clear()


class TestSanitizePathComponent:
    @pytest.mark.parametrize(
        "raw",
        [
            TRAVERSAL_SLASH,
            TRAVERSAL_BACKSLASH,
            "a/" + TRAVERSAL_SLASH,
            ABS_SLASH,
            "nul" + chr(0) + "byte",
            "...",
            "",
            "   ",
        ],
    )
    def test_no_separators_or_traversal_escape(self, raw):
        result = canonical_storage.sanitize_path_component(raw, fallback="fallback.bin")
        assert "/" not in result
        assert "\\" not in result
        assert chr(0) not in result
        assert result not in {"", ".", ".."}

    def test_replaces_windows_forbidden_characters(self):
        result = canonical_storage.sanitize_path_component(
            'a<b>c:d"e|f?g*h', fallback="x"
        )
        assert result == "a_b_c_d_e_f_g_h"

    def test_fallback_for_none(self):
        assert canonical_storage.sanitize_path_component(None, fallback="fb") == "fb"

    def test_truncates_by_bytes_keeping_extension(self):
        result = canonical_storage.sanitize_path_component(
            "あ" * 300 + ".pdf", fallback="x"
        )
        assert len(result.encode("utf-8")) <= 200
        assert result.endswith(".pdf")

    def test_normalizes_unicode(self):
        decomposed = "e\u0301clair.pdf"
        assert (
            canonical_storage.sanitize_path_component(decomposed, fallback="x")
            == "éclair.pdf"
        )


class TestRelativePaths:
    def test_canonical_path_is_scoped_by_org_document_and_version(self):
        document = _make_document()
        path = canonical_storage.canonical_relative_path(document)
        assert path == f"canonical/{ORG_ID}/{document.id}/v1/test.pdf"

    def test_work_area_path_is_scoped_by_receipt_number(self):
        document = _make_document()
        path = canonical_storage.work_area_relative_path(document, "R-2026-0001")
        assert path.startswith("work-areas/R-2026-0001/")
        assert path.endswith("/test.pdf")

    def test_work_area_receipt_is_sanitized(self):
        document = _make_document()
        path = canonical_storage.work_area_relative_path(document, TRAVERSAL_SLASH)
        assert ".." not in path
        assert path.startswith("work-areas/")


class TestFilesystemBackend:
    def test_store_canonical_writes_actual_file(self, storage_root):
        document = _make_document()

        result = asyncio.run(canonical_storage.store_canonical(document))

        target = storage_root / result.relative_path
        assert target.exists()
        assert target.read_bytes() == b"hello world"
        assert result.size_bytes == 11
        assert result.backend == "filesystem"
        assert stat.S_IMODE(os.stat(target).st_mode) == 0o640

    def test_store_work_area_writes_actual_file(self, storage_root):
        document = _make_document()
        result = asyncio.run(canonical_storage.store_work_area(document, "R-2026-0001"))

        target = storage_root / result.relative_path
        assert target.exists()
        assert target.read_bytes() == b"hello world"
        assert "work-areas/R-2026-0001" in result.relative_path

    def test_no_temporary_files_left_behind(self, storage_root):
        document = _make_document()
        asyncio.run(canonical_storage.store_canonical(document))

        assert list(storage_root.rglob("*.part")) == []
        assert list(storage_root.rglob(".transfer-*")) == []

    def test_missing_source_object_raises(self, storage_root, monkeypatch):
        monkeypatch.setattr(storage_service, "get_file_stream", lambda key: None)
        document = _make_document()

        with pytest.raises(canonical_storage.StorageTransferError) as excinfo:
            asyncio.run(canonical_storage.store_canonical(document))

        assert excinfo.value.code == "SOURCE_FILE_NOT_FOUND"
        assert excinfo.value.status_code == 502

    def test_object_storage_failure_raises_503(self, storage_root, monkeypatch):
        def _boom(key):
            raise RuntimeError("connection refused")

        monkeypatch.setattr(storage_service, "get_file_stream", _boom)
        document = _make_document()

        with pytest.raises(canonical_storage.StorageTransferError) as excinfo:
            asyncio.run(canonical_storage.store_canonical(document))

        assert excinfo.value.code == "SOURCE_STORAGE_UNAVAILABLE"
        assert excinfo.value.status_code == 503

    def test_write_failure_does_not_leave_partial_file(self, storage_root, monkeypatch):
        class _BrokenStream:
            def read(self, size):
                raise OSError("stream failure")

            def close(self):
                pass

        monkeypatch.setattr(
            storage_service, "get_file_stream", lambda key: _BrokenStream()
        )
        document = _make_document()

        with pytest.raises(canonical_storage.StorageTransferError):
            asyncio.run(canonical_storage.store_canonical(document))

        assert list(storage_root.rglob(".transfer-*")) == []


class TestNotConfigured:
    def test_fails_closed_when_no_backend_configured(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.delenv("CANONICAL_STORAGE_ROOT", raising=False)
        monkeypatch.setenv("ONEDRIVE_ENABLED", "false")
        monkeypatch.setattr(
            storage_service, "get_file_stream", lambda key: io.BytesIO(b"x")
        )
        document = _make_document()

        with pytest.raises(canonical_storage.StorageTransferError) as excinfo:
            asyncio.run(canonical_storage.store_canonical(document))
        get_settings.cache_clear()

        assert excinfo.value.code == "STORAGE_NOT_CONFIGURED"
        assert excinfo.value.status_code == 503

    def test_onedrive_enabled_without_credentials_fails_closed(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("ONEDRIVE_ENABLED", "true")
        monkeypatch.delenv("ONEDRIVE_TENANT_ID", raising=False)
        monkeypatch.delenv("ONEDRIVE_CLIENT_ID", raising=False)
        monkeypatch.delenv("ONEDRIVE_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("ONEDRIVE_DRIVE_ID", raising=False)
        monkeypatch.setenv("CANONICAL_STORAGE_ROOT", "/tmp/ignored")
        document = _make_document()

        with pytest.raises(canonical_storage.StorageTransferError) as excinfo:
            asyncio.run(canonical_storage.store_canonical(document))
        get_settings.cache_clear()

        assert excinfo.value.code == "STORAGE_NOT_CONFIGURED"
        assert "ONEDRIVE_TENANT_ID" in excinfo.value.message
        assert "ONEDRIVE_DRIVE_ID" in excinfo.value.message


class TestPathContainment:
    def test_target_never_escapes_root(self, tmp_path):
        root = Path(tmp_path).resolve()
        target = canonical_storage._contained_target(
            root, "canonical/org/doc/v1/file.pdf"
        )
        assert root in target.parents

    def test_escaping_relative_path_rejected(self, tmp_path):
        root = Path(tmp_path).resolve()
        with pytest.raises(canonical_storage.StorageTransferError):
            canonical_storage._contained_target(root, ".." + "/" + "outside.pdf")
