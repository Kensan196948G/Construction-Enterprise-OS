"""CEO-OS Event Core - Kafka Event Bus Infrastructure"""

from ceo_os_event_core.types import EventTypes, TOPIC_MAP
from ceo_os_event_core.models import (
    CloudEvent,
    create_user_event,
    create_document_event,
    create_iot_event,
    create_workflow_event,
)


def get_publisher(*args, **kwargs):
    """Lazy import for EventPublisher (requires aiokafka)"""
    from ceo_os_event_core.publisher import EventPublisher
    return EventPublisher(*args, **kwargs)


def get_subscriber(*args, **kwargs):
    """Lazy import for EventSubscriber (requires aiokafka)"""
    from ceo_os_event_core.subscriber import EventSubscriber
    return EventSubscriber(*args, **kwargs)


__all__ = [
    "EventTypes",
    "TOPIC_MAP",
    "CloudEvent",
    "create_user_event",
    "create_document_event",
    "create_iot_event",
    "create_workflow_event",
    "get_publisher",
    "get_subscriber",
]
