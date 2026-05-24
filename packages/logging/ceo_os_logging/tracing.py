"""OpenTelemetry tracing integration for CEO-OS.

This is a simplified version that can be enhanced later with actual
OpenTelemetry exporters (Jaeger, Zipkin, OTLP).
"""

from contextvars import ContextVar
import uuid

# Context variable for trace propagation
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
span_id_var: ContextVar[str] = ContextVar("span_id", default="")


def generate_trace_id() -> str:
    """Generate a new trace ID."""
    return str(uuid.uuid4())


def generate_span_id() -> str:
    """Generate a new span ID."""
    return str(uuid.uuid4())[:16]


def get_current_trace_id() -> str:
    """Get the current trace ID from context."""
    return trace_id_var.get() or ""


def set_current_trace_id(trace_id: str) -> None:
    """Set the current trace ID in context."""
    trace_id_var.set(trace_id)


def get_current_span_id() -> str:
    """Get the current span ID from context."""
    return span_id_var.get() or ""


def set_current_span_id(span_id: str) -> None:
    """Set the current span ID in context."""
    span_id_var.set(span_id)
