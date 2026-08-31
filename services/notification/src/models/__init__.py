"""通知 データモデル"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    __table_args__ = (
        Index("ix_notification_templates_code", "code", unique=True),
        Index("ix_notification_templates_category", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    channels: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=["in_app", "email"]
    )
    title_template: Mapped[str] = mapped_column(Text, nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        Enum("low", "normal", "high", "urgent", name="notification_priority"),
        default="normal",
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="template"
    )


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_recipient_id", "recipient_id"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_created_at", "created_at"),
        Index("ix_notifications_idempotency_key", "idempotency_key", unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notification.notification_templates.id"),
        nullable=True,
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    channels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "sent", "read", "failed", name="notification_status"),
        default="pending",
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    template: Mapped[NotificationTemplate | None] = relationship(
        "NotificationTemplate", back_populates="notifications"
    )
