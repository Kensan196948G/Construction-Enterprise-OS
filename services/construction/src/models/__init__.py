"""施工管理 データモデル — construction スキーマ"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class WBSItem(Base):
    """WBS (Work Breakdown Structure)"""
    __tablename__ = "wbs_items"
    __table_args__ = (
        Index("ix_wbs_items_organization_id", "organization_id"),
        Index("ix_wbs_items_project_id", "project_id"),
        Index("ix_wbs_items_parent_id", "parent_id"),
        Index("ix_wbs_items_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("construction.wbs_items.id")
    )
    wbs_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_end: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_end: Mapped[date | None] = mapped_column(Date)
    planned_cost: Mapped[float | None] = mapped_column(Numeric(15, 2))
    actual_cost: Mapped[float | None] = mapped_column(Numeric(15, 2))
    weight_percent: Mapped[float | None] = mapped_column(Numeric(5, 2))
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    responsible_person: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    children: Mapped[list["WBSItem"]] = relationship("WBSItem", backref="parent", remote_side="WBSItem.id")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="wbs_item")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="wbs_item")
    method_statements: Mapped[list["MethodStatement"]] = relationship("MethodStatement", back_populates="wbs_item")


class Resource(Base):
    """資源管理（人・機械・資材）"""
    __tablename__ = "resources"
    __table_args__ = (
        Index("ix_resources_organization_id", "organization_id"),
        Index("ix_resources_project_id", "project_id"),
        Index("ix_resources_wbs_item_id", "wbs_item_id"),
        Index("ix_resources_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    wbs_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("construction.wbs_items.id")
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    specification: Mapped[str | None] = mapped_column(String(500))
    unit: Mapped[str | None] = mapped_column(String(50))
    planned_quantity: Mapped[float | None] = mapped_column(Numeric(15, 2))
    actual_quantity: Mapped[float | None] = mapped_column(Numeric(15, 2))
    unit_cost: Mapped[float | None] = mapped_column(Numeric(15, 2))
    total_cost: Mapped[float | None] = mapped_column(Numeric(15, 2))
    allocation_start: Mapped[date | None] = mapped_column(Date)
    allocation_end: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    wbs_item: Mapped["WBSItem"] = relationship("WBSItem", back_populates="resources")


class Schedule(Base):
    """工程スケジュール"""
    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_organization_id", "organization_id"),
        Index("ix_schedules_project_id", "project_id"),
        Index("ix_schedules_wbs_item_id", "wbs_item_id"),
        Index("ix_schedules_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    wbs_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("construction.wbs_items.id")
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    planned_start: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_end: Mapped[date | None] = mapped_column(Date)
    duration_days: Mapped[int | None] = mapped_column(Integer)
    predecessor_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=[])
    successor_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), default=[])
    float_days: Mapped[int | None] = mapped_column(Integer)
    critical_path: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    wbs_item: Mapped["WBSItem"] = relationship("WBSItem", back_populates="schedules")


class MethodStatement(Base):
    """施工計画書/施工方法書"""
    __tablename__ = "method_statements"
    __table_args__ = (
        Index("ix_method_statements_organization_id", "organization_id"),
        Index("ix_method_statements_project_id", "project_id"),
        Index("ix_method_statements_wbs_item_id", "wbs_item_id"),
        Index("ix_method_statements_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    wbs_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("construction.wbs_items.id")
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    safety_measures: Mapped[str | None] = mapped_column(Text)
    environmental_measures: Mapped[str | None] = mapped_column(Text)
    quality_control_points: Mapped[str | None] = mapped_column(Text)
    required_equipment: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    required_materials: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    required_labor: Mapped[str | None] = mapped_column(Text)
    attachments: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    status: Mapped[str] = mapped_column(String(20), default="draft")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    wbs_item: Mapped["WBSItem"] = relationship("WBSItem", back_populates="method_statements")
