"""Additional structlog processors for Construction-Enterprise-OS."""

import os
import socket


def add_service_context(_, __, event_dict):
    """Add service metadata to all log entries."""
    event_dict["service"] = os.environ.get("SERVICE_NAME", "unknown")
    event_dict["host"] = socket.gethostname()
    event_dict["environment"] = os.environ.get("ENVIRONMENT", "development")
    return event_dict


def mask_sensitive_data(_, __, event_dict):
    """Mask sensitive fields in log output."""
    sensitive_keys = {"password", "token", "secret", "api_key", "credential", "authorization"}
    for key in list(event_dict.keys()):
        key_lower = key.lower()
        if any(s in key_lower for s in sensitive_keys):
            event_dict[key] = "***MASKED***"
    return event_dict


def add_user_context(user_id: str | None = None, org_id: str | None = None):
    """Create a processor that adds user context."""
    def processor(_, __, event_dict):
        if user_id:
            event_dict["user_id"] = user_id
        if org_id:
            event_dict["org_id"] = org_id
        return event_dict
    return processor
