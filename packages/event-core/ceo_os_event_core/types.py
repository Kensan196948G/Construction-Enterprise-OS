class EventTypes:
    # Auth events
    USER_CREATED = "ceo-os.user.created"
    USER_LOGIN = "ceo-os.user.login"
    USER_ROLE_CHANGED = "ceo-os.user.role_changed"
    USER_DEACTIVATED = "ceo-os.user.deactivated"

    # Document events
    DOCUMENT_UPLOADED = "ceo-os.document.uploaded"
    DOCUMENT_APPROVED = "ceo-os.document.approved"
    DOCUMENT_REJECTED = "ceo-os.document.rejected"
    DOCUMENT_VERSIONED = "ceo-os.document.versioned"
    DOCUMENT_DELETED = "ceo-os.document.deleted"

    # Workflow events
    WORKFLOW_STARTED = "ceo-os.workflow.started"
    WORKFLOW_APPROVED = "ceo-os.workflow.approved"
    WORKFLOW_REJECTED = "ceo-os.workflow.rejected"
    WORKFLOW_CANCELLED = "ceo-os.workflow.cancelled"
    WORKFLOW_ESCALATED = "ceo-os.workflow.escalated"

    # Project events
    PROJECT_CREATED = "ceo-os.project.created"
    PROJECT_STATUS_CHANGED = "ceo-os.project.status_changed"
    PROJECT_COMPLETED = "ceo-os.project.completed"

    # IoT events
    IOT_TELEMETRY = "ceo-os.iot.telemetry"
    IOT_ALERT = "ceo-os.iot.alert"
    IOT_DEVICE_ONLINE = "ceo-os.iot.device.online"
    IOT_DEVICE_OFFLINE = "ceo-os.iot.device.offline"
    IOT_THRESHOLD_EXCEEDED = "ceo-os.iot.threshold_exceeded"

    # Safety events
    SAFETY_INCIDENT_REPORTED = "ceo-os.safety.incident_reported"
    SAFETY_ALERT = "ceo-os.safety.alert"
    SAFETY_INSPECTION_COMPLETED = "ceo-os.safety.inspection_completed"

    # Notification events
    NOTIFICATION_SEND = "ceo-os.notification.send"
    NOTIFICATION_DELIVERED = "ceo-os.notification.delivered"
    NOTIFICATION_READ = "ceo-os.notification.read"


# Topic mapping: event type prefix -> Kafka topic name
TOPIC_MAP = {
    "ceo-os.user": "ceo-os.users",
    "ceo-os.document": "ceo-os.documents",
    "ceo-os.workflow": "ceo-os.workflows",
    "ceo-os.project": "ceo-os.projects",
    "ceo-os.iot": "ceo-os.iot",
    "ceo-os.safety": "ceo-os.safety",
    "ceo-os.notification": "ceo-os.notifications",
}
