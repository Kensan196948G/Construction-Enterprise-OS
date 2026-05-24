"""AI サービス テスト"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models.base import get_db


class MockScalarResult:
    def __init__(self, value=None):
        self._value = value
        self.rowcount = 0

    def scalar_one_or_none(self):
        return self._value

    def scalar(self):
        return self._value if self._value is not None else 0

    def scalars(self):
        return self

    def all(self):
        if self._value is None:
            return []
        return self._value if isinstance(self._value, list) else [self._value]

    def first(self):
        return self._value if not isinstance(self._value, list) else (self._value[0] if self._value else None)

    def fetchall(self):
        if self._value is None:
            return []
        return self._value if isinstance(self._value, list) else [self._value]


class MockResult:
    def __init__(self, value=None):
        self._value = value
        self.rowcount = 0

    def scalar_one_or_none(self):
        return self._value

    def scalar(self):
        return self._value if self._value is not None else 0

    def scalars(self):
        return self

    def all(self):
        if self._value is None:
            return []
        return self._value if isinstance(self._value, list) else [self._value]

    def first(self):
        return self._value if not isinstance(self._value, list) else (self._value[0] if self._value else None)

    def fetchall(self):
        if self._value is None:
            return []
        return self._value if isinstance(self._value, list) else [self._value]


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
    mock_db.delete = AsyncMock()

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
        "scopes": ["ai:read", "ai:write"],
    }
    token = jwt.encode(payload, settings.jwt_public_key, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-service"


class TestAuthRequired:
    endpoints = [
        ("GET", "/api/v1/ai/prompts"),
        ("POST", "/api/v1/ai/chat"),
        ("POST", "/api/v1/ai/chat/stream"),
        ("POST", "/api/v1/ai/complete"),
        ("POST", "/api/v1/ai/rag/search"),
        ("POST", "/api/v1/ai/rag/generate"),
        ("POST", "/api/v1/ai/embeddings"),
        ("POST", "/api/v1/ai/embeddings/search"),
    ]

    def test_all_endpoints_require_auth(self, client):
        for method, url in self.endpoints:
            if method == "GET":
                response = client.get(url)
            else:
                response = client.post(url, json={})
            assert response.status_code == 401, f"{method} {url} returned {response.status_code}"

    def test_delete_embeddings_requires_auth(self, client):
        response = client.delete(f"/api/v1/ai/embeddings/document/{uuid4()}")
        assert response.status_code == 401

    def test_prompt_detail_requires_auth(self, client):
        response = client.get(f"/api/v1/ai/prompts/{uuid4()}")
        assert response.status_code == 401

    def test_prompt_update_requires_auth(self, client):
        response = client.put(f"/api/v1/ai/prompts/{uuid4()}", json={"name": "Test"})
        assert response.status_code == 401

    def test_prompt_delete_requires_auth(self, client):
        response = client.delete(f"/api/v1/ai/prompts/{uuid4()}")
        assert response.status_code == 401


class TestPromptTemplateCRUD:
    def test_create_prompt_template(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/prompts",
            json={
                "name": "Test Template",
                "description": "Test description",
                "category": "general",
                "system_prompt": "You are a helpful assistant.",
                "user_prompt_template": "Question: {{ question }}",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Template"

    def test_list_prompt_templates(self, client):
        headers = _auth_headers()
        response = client.get("/api/v1/ai/prompts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestLLMService:
    def test_mock_llm_complete(self):
        from src.services.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        import asyncio
        result = asyncio.run(provider.complete([
            {"role": "user", "content": "Hello, how are you?"}
        ]))
        assert "Mock response to:" in result
        assert "Hello" in result

    def test_mock_llm_stream(self):
        from src.services.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        import asyncio

        async def collect_stream():
            chunks = []
            async for chunk in provider.stream_complete([
                {"role": "user", "content": "Hello world"}
            ]):
                chunks.append(chunk)
            return "".join(chunks)

        result = asyncio.run(collect_stream())
        assert "Mock response to:" in result
        assert "Hello" in result

    def test_openai_provider_init(self):
        from src.services.llm_service import OpenAICompatibleProvider

        provider = OpenAICompatibleProvider(
            base_url="https://test.api.com/v1",
            api_key="test-key",
            default_model="gpt-3.5-turbo",
        )
        assert provider.base_url == "https://test.api.com/v1"
        assert provider.api_key == "test-key"
        assert provider.default_model == "gpt-3.5-turbo"

    def test_chat_endpoint_with_mock(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What is the safest way to excavate?"}
                ],
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Mock response to:" in data["data"]["message"]["content"]

    def test_chat_stream_endpoint(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/chat/stream",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_complete_endpoint_not_found(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/complete",
            json={
                "prompt_template_id": str(uuid4()),
                "variables": {},
            },
            headers=headers,
        )
        assert response.status_code == 404


class TestTextChunking:
    def test_chunk_text_basic(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")
        text = "This is a test. " * 100
        chunks = service.chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 100

    def test_chunk_text_short(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")
        text = "Short text."
        chunks = service.chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_empty(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")
        chunks = service.chunk_text("   ", chunk_size=500, overlap=50)
        assert len(chunks) == 0

    def test_chunk_text_exact_size(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")
        text = "A" * 500
        chunks = service.chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == text


class TestMockEmbedding:
    def test_mock_embedding_dimensions(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")

        import asyncio
        vec = asyncio.run(service.mock_embedding("test text"))
        assert len(vec) == 1536
        assert all(-1.0 <= v <= 1.0 for v in vec)

    def test_mock_embedding_different_texts(self):
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService(base_url="http://test", api_key="test")

        import asyncio
        vec1 = asyncio.run(service.mock_embedding("text one"))
        vec2 = asyncio.run(service.mock_embedding("text two"))
        assert vec1 != vec2


class TestRAGService:
    def test_semantic_search_mock(self):
        from unittest.mock import AsyncMock
        from src.services.embedding_service import EmbeddingService
        from src.services.llm_service import MockLLMProvider
        from src.services.rag_service import RAGService

        embedding_service = EmbeddingService(base_url="http://test", api_key="test")
        llm = MockLLMProvider()
        rag_service = RAGService(embedding_service, llm)

        import asyncio

        async def run_search():
            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(return_value=MockScalarResult([]))
            return await rag_service.semantic_search(
                db=mock_db,
                query="safety regulations",
                top_k=3,
                use_mock=True,
            )

        results = asyncio.run(run_search())
        assert isinstance(results, list)

    def test_generate_with_context_mock(self):
        from src.services.embedding_service import EmbeddingService
        from src.services.llm_service import MockLLMProvider
        from src.services.rag_service import RAGService

        embedding_service = EmbeddingService(base_url="http://test", api_key="test")
        llm = MockLLMProvider()
        rag_service = RAGService(embedding_service, llm)

        import asyncio

        async def run_generate():
            return await rag_service.generate_with_context(
                db=None,
                query="What are the safety rules?",
                context_chunks=[
                    {"content": "Always wear a hard hat.", "similarity": 0.95},
                    {"content": "Follow safety protocols.", "similarity": 0.88},
                ],
            )

        answer, sources = asyncio.run(run_generate())
        assert "Mock response to:" in answer
        assert len(sources) == 2


class TestDefaultPrompts:
    def test_default_templates_exist(self):
        from src.services.prompt_service import DEFAULT_TEMPLATES

        assert len(DEFAULT_TEMPLATES) == 5
        names = [t["name"] for t in DEFAULT_TEMPLATES]
        assert "safety_report_assistant" in names
        assert "construction_qa" in names
        assert "document_summarizer" in names
        assert "specification_checker" in names
        assert "hazard_predictor" in names

    def test_default_templates_have_required_fields(self):
        from src.services.prompt_service import DEFAULT_TEMPLATES

        required = ["name", "description", "category", "system_prompt", "user_prompt_template"]
        for tmpl in DEFAULT_TEMPLATES:
            for field in required:
                assert field in tmpl, f"Missing {field} in {tmpl['name']}"
                assert tmpl[field], f"Empty {field} in {tmpl['name']}"


class TestRAGSearchEndpoint:
    def test_rag_search_endpoint(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/rag/search",
            json={
                "query": "safety regulations for construction",
                "top_k": 3,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_rag_generate_endpoint(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/rag/generate",
            json={
                "query": "What are the safety regulations?",
                "top_k": 3,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "answer" in data["data"]


class TestEmbeddingEndpoint:
    def test_create_embeddings_endpoint(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/embeddings",
            json={
                "source_type": "document",
                "source_id": str(uuid4()),
                "content": "This is a test document about construction safety.",
                "chunk_size": 500,
                "chunk_overlap": 50,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_search_embeddings_endpoint(self, client):
        headers = _auth_headers()
        response = client.post(
            "/api/v1/ai/embeddings/search",
            json={
                "query": "safety regulations",
                "top_k": 5,
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_embeddings_endpoint(self, client):
        headers = _auth_headers()
        response = client.delete(
            f"/api/v1/ai/embeddings/document/{uuid4()}",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
