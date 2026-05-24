"""Platform関連 SQLAlchemy モデル"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ViewerConfig(Base):
    __tablename__ = "viewer_configs"
    __table_args__ = (
        Index("ix_viewer_configs_org", "organization_id"),
        Index("ix_viewer_configs_project", "project_id"),
        Index("ix_viewer_configs_type", "viewer_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    viewer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_ids: Mapped[list] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)
    layer_ids: Mapped[list] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)
    camera_state: Mapped[dict] = mapped_column(JSONB, default=dict)
    visible_categories: Mapped[list] = mapped_column(ARRAY(Text), default=list)
    clipping_planes: Mapped[dict] = mapped_column(JSONB, default=dict)
    theme: Mapped[str] = mapped_column(String(20), default="light")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    scenes: Mapped[list["ViewerScene"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )


class ViewerScene(Base):
    __tablename__ = "viewer_scenes"
    __table_args__ = (
        Index("ix_viewer_scenes_config", "config_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform.viewer_configs.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    camera_state: Mapped[dict] = mapped_column(JSONB, nullable=False)
    annotations: Mapped[list] = mapped_column(JSONB, default=list)
    measurements: Mapped[list] = mapped_column(JSONB, default=list)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    config: Mapped["ViewerConfig"] = relationship(back_populates="scenes")


class IoTDashboard(Base):
    __tablename__ = "iot_dashboards"
    __table_args__ = (
        Index("ix_iot_dashboards_org", "organization_id"),
        Index("ix_iot_dashboards_project", "project_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout: Mapped[dict] = mapped_column(JSONB, nullable=False)
    refresh_interval_seconds: Mapped[int] = mapped_column(Integer, default=10)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DeviceGroup(Base):
    __tablename__ = "device_groups"
    __table_args__ = (
        Index("ix_device_groups_org", "organization_id"),
        Index("ix_device_groups_parent", "parent_group_id"),
        Index("ix_device_groups_type", "group_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_ids: Mapped[list] = mapped_column(ARRAY(UUID(as_uuid=True)), default=list)
    group_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform.device_groups.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    parent_group: Mapped["DeviceGroup | None"] = relationship(
        "DeviceGroup", remote_side="DeviceGroup.id", back_populates="children"
    )
    children: Mapped[list["DeviceGroup"]] = relationship(
        "DeviceGroup", back_populates="parent_group"
    )
