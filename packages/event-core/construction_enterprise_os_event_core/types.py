class EventTypes:
    # Auth events
    USER_CREATED = "construction-enterprise-os.user.created"
    USER_LOGIN = "construction-enterprise-os.user.login"
    USER_ROLE_CHANGED = "construction-enterprise-os.user.role_changed"
    USER_DEACTIVATED = "construction-enterprise-os.user.deactivated"

    # Document events
    DOCUMENT_UPLOADED = "construction-enterprise-os.document.uploaded"
    DOCUMENT_APPROVED = "construction-enterprise-os.document.approved"
    DOCUMENT_REJECTED = "construction-enterprise-os.document.rejected"
    DOCUMENT_VERSIONED = "construction-enterprise-os.document.versioned"
    DOCUMENT_DELETED = "construction-enterprise-os.document.deleted"

    # Workflow events
    WORKFLOW_STARTED = "construction-enterprise-os.workflow.started"
    WORKFLOW_APPROVED = "construction-enterprise-os.workflow.approved"
    WORKFLOW_REJECTED = "construction-enterprise-os.workflow.rejected"
    WORKFLOW_CANCELLED = "construction-enterprise-os.workflow.cancelled"
    WORKFLOW_ESCALATED = "construction-enterprise-os.workflow.escalated"

    # Project events
    PROJECT_CREATED = "construction-enterprise-os.project.created"
    PROJECT_STATUS_CHANGED = "construction-enterprise-os.project.status_changed"
    PROJECT_COMPLETED = "construction-enterprise-os.project.completed"

    # IoT events
    IOT_TELEMETRY = "construction-enterprise-os.iot.telemetry"
    IOT_ALERT = "construction-enterprise-os.iot.alert"
    IOT_DEVICE_ONLINE = "construction-enterprise-os.iot.device.online"
    IOT_DEVICE_OFFLINE = "construction-enterprise-os.iot.device.offline"
    IOT_THRESHOLD_EXCEEDED = "construction-enterprise-os.iot.threshold_exceeded"

    # Safety events
    SAFETY_INCIDENT_REPORTED = "construction-enterprise-os.safety.incident_reported"
    SAFETY_ALERT = "construction-enterprise-os.safety.alert"
    SAFETY_INSPECTION_COMPLETED = "construction-enterprise-os.safety.inspection_completed"

    # Notification events
    NOTIFICATION_SEND = "construction-enterprise-os.notification.send"
    NOTIFICATION_DELIVERED = "construction-enterprise-os.notification.delivered"
    NOTIFICATION_READ = "construction-enterprise-os.notification.read"


# Topic mapping: event type prefix -> Kafka topic name
TOPIC_MAP = {
    "construction-enterprise-os.user": "construction-enterprise-os.users",
    "construction-enterprise-os.document": "construction-enterprise-os.documents",
    "construction-enterprise-os.workflow": "construction-enterprise-os.workflows",
    "construction-enterprise-os.project": "construction-enterprise-os.projects",
    "construction-enterprise-os.iot": "construction-enterprise-os.iot",
    "construction-enterprise-os.safety": "construction-enterprise-os.safety",
    "construction-enterprise-os.notification": "construction-enterprise-os.notifications",
}
