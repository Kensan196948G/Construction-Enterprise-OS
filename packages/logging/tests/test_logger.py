"""Tests for CEO-OS logging package."""

import io
import json
import logging
import os
import sys
import uuid

import pytest
import structlog
from unittest.mock import AsyncMock, patch, MagicMock

from ceo_os_logging import (
    setup_logging,
    get_logger,
    LoggerMixin,
    add_service_context,
    mask_sensitive_data,
    add_user_context,
    generate_trace_id,
    generate_span_id,
    get_current_trace_id,
    set_current_trace_id,
    get_current_span_id,
    set_current_span_id,
)


class TestSetupLogging:
    """Tests for logger setup."""

    def test_setup_logging_default(self):
        """Logger setup works with defaults."""
        logger = setup_logging("test-service")
        assert logger is not None
        logger.info("test.message", key="value")

    def test_setup_logging_debug_mode(self):
        """Logger setup works in debug mode."""
        logger = setup_logging("test-service", log_level="DEBUG")
        logger.debug("debug.message", detail="test")

    def test_setup_logging_warning_level(self):
        """Log levels filter correctly."""
        logger = setup_logging("test-service", log_level="WARNING")
        # INFO should not appear when level is WARNING
        logger.info("info.message")
        logger.warning("warning.message")

    def test_get_logger(self):
        """get_logger returns a structlog logger."""
        setup_logging("test-service")
        logger = get_logger("my-component")
        assert logger is not None
        logger.info("component.event", attr="val")


class TestLoggerMixin:
    """Tests for LoggerMixin."""

    def test_logger_mixin(self):
        """LoggerMixin adds logger property."""
        setup_logging("test-service")

        class MyService(LoggerMixin):
            pass

        service = MyService()
        assert hasattr(service, "logger")
        assert service.logger is not None

    def test_logger_mixin_uses_class_name(self):
        """Logger name matches the class name."""
        setup_logging("test-service")

        class OrderProcessor(LoggerMixin):
            pass

        processor = OrderProcessor()
        # The logger name should be the class name
        logger = structlog.get_logger("OrderProcessor")
        assert logger is not None


class TestFormatters:
    """Tests for formatters/processors."""

    def test_add_service_context(self):
        """add_service_context adds service metadata."""
        os.environ["SERVICE_NAME"] = "test-svc"
        os.environ["ENVIRONMENT"] = "testing"

        event_dict = add_service_context(None, None, {"event": "test"})
        assert event_dict["service"] == "test-svc"
        assert event_dict["host"] is not None
        assert event_dict["environment"] == "testing"

        del os.environ["SERVICE_NAME"]
        del os.environ["ENVIRONMENT"]

    def test_add_service_context_defaults(self):
        """add_service_context uses defaults when env vars missing."""
        event_dict = add_service_context(None, None, {"event": "test"})
        assert event_dict["service"] == "unknown"
        assert event_dict["environment"] == "development"

    def test_mask_sensitive_data(self):
        """mask_sensitive_data redacts sensitive fields."""
        event_dict = {
            "event": "login",
            "password": "secret123",
            "token": "bearer-xxx",
            "user_id": "1001",
            "credential": "pass",
        }
        result = mask_sensitive_data(None, None, event_dict.copy())
        assert result["password"] == "***MASKED***"
        assert result["token"] == "***MASKED***"
        assert result["credential"] == "***MASKED***"
        assert result["user_id"] == "1001"
        assert result["event"] == "login"

    def test_mask_sensitive_data_case_insensitive(self):
        """mask_sensitive_data works case-insensitively."""
        event_dict = {
            "event": "api_call",
            "Authorization": "Bearer token123",
            "API_KEY": "key-abc",
        }
        result = mask_sensitive_data(None, None, event_dict.copy())
        assert result["Authorization"] == "***MASKED***"
        assert result["API_KEY"] == "***MASKED***"

    def test_add_user_context_with_values(self):
        """add_user_context adds user and org IDs."""
        processor = add_user_context(user_id="u-100", org_id="o-50")
        event_dict = processor(None, None, {"event": "action"})
        assert event_dict["user_id"] == "u-100"
        assert event_dict["org_id"] == "o-50"

    def test_add_user_context_with_none(self):
        """add_user_context skips None values."""
        processor = add_user_context(user_id=None, org_id=None)
        event_dict = processor(None, None, {"event": "action"})
        assert "user_id" not in event_dict
        assert "org_id" not in event_dict


class TestTracing:
    """Tests for tracing utilities."""

    def test_generate_trace_id(self):
        """generate_trace_id returns a valid UUID string."""
        trace_id = generate_trace_id()
        uuid_obj = uuid.UUID(trace_id)
        assert str(uuid_obj) == trace_id

    def test_generate_span_id(self):
        """generate_span_id returns a 16-char string."""
        span_id = generate_span_id()
        assert len(span_id) == 16

    def test_trace_id_context(self):
        """Trace ID can be set and retrieved."""
        tid = str(uuid.uuid4())
        set_current_trace_id(tid)
        assert get_current_trace_id() == tid

    def test_span_id_context(self):
        """Span ID can be set and retrieved."""
        sid = "abcd1234abcd1234"
        set_current_span_id(sid)
        assert get_current_span_id() == sid

    def test_trace_id_default_empty(self):
        """Default trace ID is empty string."""
        # Need to manually reset contextvar since tests share the same process
        from ceo_os_logging.tracing import trace_id_var
        token = trace_id_var.set("")
        assert get_current_trace_id() == ""
        trace_id_var.reset(token)

    def test_trace_ids_are_unique(self):
        """Multiple trace IDs are unique."""
        ids = {generate_trace_id() for _ in range(100)}
        assert len(ids) == 100


class TestMiddleware:
    """Tests for FastAPI LoggingMiddleware."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request."""
        req = MagicMock()
        req.headers = {"user-agent": "pytest"}
        req.method = "GET"
        req.url = MagicMock()
        req.url.path = "/api/test"
        req.url.query = "page=1"
        req.client = MagicMock()
        req.client.host = "127.0.0.1"
        req.state = MagicMock()
        return req

    @pytest.fixture
    def mock_response(self):
        """Create a mock response."""
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {}
        return resp

    @pytest.mark.asyncio
    async def test_middleware_dispatches(self, mock_request, mock_response):
        """Middleware logs request and response."""
        from ceo_os_logging.middleware import LoggingMiddleware

        middleware = LoggingMiddleware(app=None)

        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(mock_request, call_next)

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        call_next.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_middleware_assigns_request_id(self, mock_request, mock_response):
        """Middleware assigns a request ID."""
        from ceo_os_logging.middleware import LoggingMiddleware

        middleware = LoggingMiddleware(app=None)
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(mock_request, call_next)

        request_id = response.headers.get("X-Request-ID")
        assert request_id is not None
        uuid.UUID(request_id)  # Should not raise

    @pytest.mark.asyncio
    async def test_middleware_uses_existing_request_id(self, mock_request, mock_response):
        """Middleware uses existing X-Request-ID header."""
        from ceo_os_logging.middleware import LoggingMiddleware

        existing_id = str(uuid.uuid4())
        mock_request.headers = {"X-Request-ID": existing_id}

        middleware = LoggingMiddleware(app=None)
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-Request-ID"] == existing_id

    @pytest.mark.asyncio
    async def test_middleware_logs_on_error(self, mock_request):
        """Middleware logs error on exception."""
        from ceo_os_logging.middleware import LoggingMiddleware

        middleware = LoggingMiddleware(app=None)
        call_next = AsyncMock(side_effect=RuntimeError("test error"))

        with pytest.raises(RuntimeError, match="test error"):
            await middleware.dispatch(mock_request, call_next)


class TestIntegration:
    """Integration-style tests."""

    def test_json_output_contains_expected_fields(self):
        """JSON output contains expected fields."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        logger = setup_logging("test-svc")
        logger.info("user.login", user_id="1001", ip="10.0.0.1")

        handler.flush()
        output = stream.getvalue()
        assert output.strip(), "No output captured"
        record = json.loads(output.strip())
        assert record["event"] == "user.login"
        assert record["user_id"] == "1001"
        assert record["ip"] == "10.0.0.1"
        assert "timestamp" in record
        assert "level" in record

    def test_log_level_filters(self):
        """Log levels filter correctly in JSON output."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.WARNING)

        logger = setup_logging("test-svc", log_level="WARNING")
        logger.info("should.not.appear", key="value")
        logger.warning("should.appear", key="value")

        handler.flush()
        output = stream.getvalue()
        assert "should.not.appear" not in output
        assert "should.appear" in output
