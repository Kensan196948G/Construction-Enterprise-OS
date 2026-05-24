"""Vision service API tests."""

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
TEST_OCR_ID = uuid.uuid4()
TEST_ANALYSIS_ID = uuid.uuid4()
TEST_INDEX_ID = uuid.uuid4()

VALID_TOKEN_PAYLOAD = {
    "sub": str(TEST_USER_ID),
    "type": "user",
    "org": str(TEST_ORG_ID),
    "roles": ["vision_admin", "admin"],
    "scopes": [],
}


def _make_auth_header() -> dict:
    import base64
    import json

    payload_b64 = (
        base64.urlsafe_b64encode(json.dumps(VALID_TOKEN_PAYLOAD).encode())
        .decode()
        .rstrip("=")
    )
    header_b64 = (
        base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        .decode()
        .rstrip("=")
    )
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
        self.rowcount = len(items) if isinstance(items, list) else 0

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


class MockOCRResult:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_OCR_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.document_id = kwargs.get("document_id", None)
        self.file_key = kwargs.get("file_key", None)
        self.language = kwargs.get("language", "ja")
        self.extracted_text = kwargs.get("extracted_text", "")
        self.confidence = kwargs.get("confidence", None)
        self.page_count = kwargs.get("page_count", None)
        self.processing_time_ms = kwargs.get("processing_time_ms", None)
        self.entities = kwargs.get("entities", {})
        self.status = kwargs.get("status", "completed")
        self.error_message = kwargs.get("error_message", None)
        self.processed_by = kwargs.get("processed_by", None)
        self.created_at = kwargs.get("created_at", _utcnow())


class MockImageAnalysis:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_ANALYSIS_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.file_key = kwargs.get("file_key", "test/image.jpg")
        self.analysis_type = kwargs.get("analysis_type", "object_detection")
        self.results = kwargs.get("results", {})
        self.confidence = kwargs.get("confidence", None)
        self.processing_time_ms = kwargs.get("processing_time_ms", None)
        self.model_used = kwargs.get("model_used", None)
        self.status = kwargs.get("status", "completed")
        self.created_at = kwargs.get("created_at", _utcnow())


class MockVectorIndex:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", TEST_INDEX_ID)
        self.organization_id = kwargs.get("organization_id", TEST_ORG_ID)
        self.collection_name = kwargs.get("collection_name", "documents")
        self.dimension = kwargs.get("dimension", 1536)
        self.index_type = kwargs.get("index_type", "ivfflat")
        self.metric = kwargs.get("metric", "cosine")
        self.document_count = kwargs.get("document_count", 0)
        self.total_vectors = kwargs.get("total_vectors", 0)
        self.is_active = kwargs.get("is_active", True)
        self.created_at = kwargs.get("created_at", _utcnow())


# ═══════════════════════════════════════════════
# Test 1: Health check
# ═══════════════════════════════════════════════

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "vision-service"


# ═══════════════════════════════════════════════
# Test 2-4: Auth required for endpoints
# ═══════════════════════════════════════════════

def test_ocr_requires_auth(client):
    response = client.get("/api/v1/ocr/results")
    assert response.status_code == 401


def test_image_analysis_requires_auth(client):
    response = client.get("/api/v1/vision/analyses")
    assert response.status_code == 401


def test_vectors_require_auth(client):
    response = client.get("/api/v1/vectors/indices")
    assert response.status_code == 401


# ═══════════════════════════════════════════════
# Test 5-7: OCR CRUD
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_submit_ocr_process(mock_jwt, app):
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
        "/api/v1/ocr/process",
        json={
            "organization_id": str(TEST_ORG_ID),
            "file_key": "documents/invoice_001.pdf",
            "language": "ja",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["status"] == "pending"
    assert data["data"]["language"] == "ja"


@patch("src.middleware.auth.jwt")
def test_list_ocr_results(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    r1 = MockOCRResult(
        id=uuid.uuid4(),
        extracted_text="請求書 No.001",
        confidence=0.95,
        status="completed",
    )
    r2 = MockOCRResult(
        id=uuid.uuid4(),
        extracted_text="見積書 2024年3月",
        confidence=0.88,
        status="completed",
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([r1, r2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/ocr/results",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_get_ocr_result_detail(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    ocr = MockOCRResult(
        id=TEST_OCR_ID,
        extracted_text="工事契約書 第3条",
        confidence=0.97,
        status="completed",
        entities={"dates": ["2024-04-01"], "amounts": ["¥5,000,000"]},
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([ocr]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        f"/api/v1/ocr/results/{TEST_OCR_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["extracted_text"] == "工事契約書 第3条"
    assert data["confidence"] == 0.97
    assert "dates" in data["entities"]


# ═══════════════════════════════════════════════
# Test 8-9: Image Analysis CRUD
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_submit_image_analysis(mock_jwt, app):
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
        "/api/v1/vision/analyze",
        json={
            "organization_id": str(TEST_ORG_ID),
            "file_key": "safety/photos/site_001.jpg",
            "analysis_type": "safety_check",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["status"] == "processing"
    assert data["data"]["analysis_type"] == "safety_check"


@patch("src.middleware.auth.jwt")
def test_list_image_analyses(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    a1 = MockImageAnalysis(
        id=uuid.uuid4(),
        analysis_type="defect_detection",
        results={"defects": [{"type": "crack", "severity": "high"}]},
    )
    a2 = MockImageAnalysis(
        id=uuid.uuid4(),
        analysis_type="worker_detection",
        results={"workers": 3, "helmets": 2},
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([a1, a2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/vision/analyses",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


# ═══════════════════════════════════════════════
# Test 10-13: Vector DB operations
# ═══════════════════════════════════════════════

@patch("src.middleware.auth.jwt")
def test_create_vector_index(mock_jwt, app):
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
        "/api/v1/vectors/indices",
        json={
            "organization_id": str(TEST_ORG_ID),
            "collection_name": "regulations",
            "dimension": 1536,
            "index_type": "hnsw",
            "metric": "cosine",
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["collection_name"] == "regulations"
    assert data["data"]["dimension"] == 1536


@patch("src.middleware.auth.jwt")
def test_list_vector_indices(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    idx1 = MockVectorIndex(
        id=uuid.uuid4(), collection_name="specifications", dimension=1536
    )
    idx2 = MockVectorIndex(
        id=uuid.uuid4(), collection_name="knowledge_base", dimension=768
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([idx1, idx2]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.get(
        "/api/v1/vectors/indices",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@patch("src.middleware.auth.jwt")
def test_semantic_search(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    vi = MockVectorIndex(id=TEST_INDEX_ID, collection_name="documents")

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([vi]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/vectors/search",
        json={
            "index_id": str(TEST_INDEX_ID),
            "query_text": "安全管理基準 高所作業",
            "top_k": 3,
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 3
    assert results[0]["similarity"] > results[1]["similarity"]


@patch("src.middleware.auth.jwt")
def test_index_documents(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    vi = MockVectorIndex(
        id=TEST_INDEX_ID, collection_name="regulations", document_count=10, total_vectors=10
    )

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([vi]))
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
        "/api/v1/vectors/index",
        json={
            "index_id": str(TEST_INDEX_ID),
            "documents": [
                {
                    "source_id": str(uuid.uuid4()),
                    "source_type": "regulation",
                    "content": "第12条 高所作業時は安全帯を着用すること。",
                    "metadata": {"chapter": "安全規定", "page": 12},
                },
                {
                    "source_id": str(uuid.uuid4()),
                    "source_type": "regulation",
                    "content": "作業開始前のKYミーティングを実施すること。",
                    "metadata": {"chapter": "安全規定", "page": 5},
                },
            ],
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["indexed_count"] == 2
    assert data["total_vectors"] == 2


@patch("src.middleware.auth.jwt")
def test_delete_vector_index(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    vi = MockVectorIndex(id=TEST_INDEX_ID)

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([vi]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.delete(
        f"/api/v1/vectors/indices/{TEST_INDEX_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True


@patch("src.middleware.auth.jwt")
def test_get_ocr_result_not_found(mock_jwt, app):
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
        f"/api/v1/ocr/results/{TEST_OCR_ID}",
        headers=_make_auth_header(),
    )
    assert response.status_code == 404


@patch("src.middleware.auth.jwt")
def test_index_documents_empty_request(mock_jwt, app):
    mock_jwt.decode.return_value = VALID_TOKEN_PAYLOAD

    vi = MockVectorIndex(id=TEST_INDEX_ID)

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=MockScalarResult([vi]))
    db_mock.commit = AsyncMock()
    db_mock.rollback = AsyncMock()
    db_mock.close = AsyncMock()

    async def get_mock_db():
        yield db_mock

    app.dependency_overrides[get_db] = get_mock_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/vectors/index",
        json={
            "index_id": str(TEST_INDEX_ID),
            "documents": [],
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 400


@patch("src.middleware.auth.jwt")
def test_semantic_search_index_not_found(mock_jwt, app):
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
    response = client.post(
        "/api/v1/vectors/search",
        json={
            "index_id": str(TEST_INDEX_ID),
            "query_text": "安全管理基準",
            "top_k": 5,
        },
        headers=_make_auth_header(),
    )
    assert response.status_code == 404
