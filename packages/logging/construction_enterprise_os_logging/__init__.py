"""Construction-Enterprise-OS Unified Logging Package.

Provides structured JSON logging via structlog for all services,
with built-in middleware for FastAPI and OpenTelemetry tracing support.

Usage:
    from construction_enterprise_os_logging import setup_logging, get_logger, LoggerMixin

    logger = setup_logging("my-service")
    logger.info("event.name", key="value")

    class MyClass(LoggerMixin):
        def do_something(self):
            self.logger.info("something.done")
"""

from construction_enterprise_os_logging.logger import setup_logging, get_logger, LoggerMixin
from construction_enterprise_os_logging.formatters import (
    add_service_context,
    mask_sensitive_data,
    add_user_context,
)
from construction_enterprise_os_logging.middleware import LoggingMiddleware
from construction_enterprise_os_logging.tracing import (
    generate_trace_id,
    generate_span_id,
    get_current_trace_id,
    set_current_trace_id,
    get_current_span_id,
    set_current_span_id,
)

__all__ = [
    # Logger
    "setup_logging",
    "get_logger",
    "LoggerMixin",
    # Formatters
    "add_service_context",
    "mask_sensitive_data",
    "add_user_context",
    # Middleware
    "LoggingMiddleware",
    # Tracing
    "generate_trace_id",
    "generate_span_id",
    "get_current_trace_id",
    "set_current_trace_id",
    "get_current_span_id",
    "set_current_span_id",
]
