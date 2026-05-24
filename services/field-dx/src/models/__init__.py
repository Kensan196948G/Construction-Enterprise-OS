"""Field DX データモデル — field スキーマ"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DailyReport(Base):
    """作業日報"""
    __tablename__ = "daily_reports"
    __table_args__ = (
        Index("ix_daily_reports_organization_id", "organization_id"),
        Index("ix_daily_reports_project_id", "project_id"),
        Index("ix_daily_reports_report_date", "report_date"),
        Index("ix_daily_reports_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    weather: Mapped[str | None] = mapped_column(String(20))
    temperature: Mapped[float | None] = mapped_column(Float)
    work_description: Mapped[str] = mapped_column(Text, nullable=False)
    work_results: Mapped[str | None] = mapped_column(Text)
    worker_count: Mapped[int | None] = mapped_column(Integer)
    equipment_used: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    materials_used: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    issues: Mapped[str | None] = mapped_column(Text)
    next_plan: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ProgressRecord(Base):
    """出来形・進捗記録"""
    __tablename__ = "progress_records"
    __table_args__ = (
        Index("ix_progress_records_organization_id", "organization_id"),
        Index("ix_progress_records_project_id", "project_id"),
        Index("ix_progress_records_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    activity_name: Mapped[str] = mapped_column(String(500), nullable=False)
    activity_code: Mapped[str | None] = mapped_column(String(100))
    planned_quantity: Mapped[float | None] = mapped_column(Float)
    actual_quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_end: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_end: Mapped[date | None] = mapped_column(Date)
    progress_percent: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class QualityCheck(Base):
    """品質管理"""
    __tablename__ = "quality_checks"
    __table_args__ = (
        Index("ix_quality_checks_organization_id", "organization_id"),
        Index("ix_quality_checks_project_id", "project_id"),
        Index("ix_quality_checks_check_date", "check_date"),
        Index("ix_quality_checks_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    check_item: Mapped[str] = mapped_column(String(500), nullable=False)
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    standard_value: Mapped[str | None] = mapped_column(String(255))
    measured_value: Mapped[str | None] = mapped_column(String(255))
    is_conforming: Mapped[bool | None] = mapped_column(Boolean)
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(500))
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
