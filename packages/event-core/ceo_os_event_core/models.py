from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
import json


@dataclass
class CloudEvent:
    """CloudEvents 1.0 compliant event"""

    type: str
    source: str
    id: str = field(default_factory=lambda: str(uuid4()))
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    subject: str | None = None
    datacontenttype: str = "application/json"
    data: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "CloudEvent":
        return cls(**json.loads(json_str))


def create_user_event(
    event_type: str, user_id: str, org_id: str, data: dict
) -> CloudEvent:
    return CloudEvent(
        type=event_type,
        source="/services/auth",
        subject=user_id,
        data={"user_id": user_id, "organization_id": org_id, **data},
    )


def create_document_event(
    event_type: str, document_id: str, user_id: str, data: dict
) -> CloudEvent:
    return CloudEvent(
        type=event_type,
        source="/services/document",
        subject=document_id,
        data={"document_id": document_id, "user_id": user_id, **data},
    )


def create_iot_event(
    event_type: str, device_id: str, data: dict
) -> CloudEvent:
    return CloudEvent(
        type=event_type,
        source="/services/iot",
        subject=device_id,
        data={"device_id": device_id, **data},
    )


def create_workflow_event(
    event_type: str, workflow_id: str, data: dict
) -> CloudEvent:
    return CloudEvent(
        type=event_type,
        source="/services/workflow",
        subject=workflow_id,
        data={"workflow_id": workflow_id, **data},
    )
