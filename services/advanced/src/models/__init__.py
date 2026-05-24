"""Advanced データモデル (MarineConstruction, InspectionRecord, DesignReview, PredictiveModel)"""

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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, NUMERIC
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MarineConstruction(Base):
    __tablename__ = "marine_construction"
    __table_args__ = (
        Index("ix_marine_construction_organization_id", "organization_id"),
        Index("ix_marine_construction_project_id", "project_id"),
        Index("ix_marine_construction_status", "status"),
        Index("ix_marine_construction_type", "construction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    construction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="planning")
    water_depth: Mapped[float | None] = mapped_column(Float)
    tide_info: Mapped[dict | None] = mapped_column(JSONB)
    wave_condition: Mapped[dict | None] = mapped_column(JSONB)
    equipment_deployed: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    material_volume: Mapped[float | None] = mapped_column("material_volume", NUMERIC(15, 2))
    progress_percent: Mapped[float | None] = mapped_column(NUMERIC(5, 2), default=0)
    location: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    supervisor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class InspectionRecord(Base):
    __tablename__ = "inspection_records"
    __table_args__ = (
        Index("ix_inspection_records_organization_id", "organization_id"),
        Index("ix_inspection_records_asset_type", "asset_type"),
        Index("ix_inspection_records_inspection_date", "inspection_date"),
        Index("ix_inspection_records_severity", "severity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(500), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    inspection_method: Mapped[str | None] = mapped_column(String(50))
    ai_model_used: Mapped[str | None] = mapped_column(String(100))
    defect_type: Mapped[str | None] = mapped_column(String(50))
    severity: Mapped[str | None] = mapped_column(String(20))
    confidence: Mapped[float | None] = mapped_column(Float)
    defect_count: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(Text)
    image_keys: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    inspector_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    inspection_date: Mapped[date] = mapped_column(Date, nullable=False)
    requires_action: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DesignReview(Base):
    __tablename__ = "design_reviews"
    __table_args__ = (
        Index("ix_design_reviews_organization_id", "organization_id"),
        Index("ix_design_reviews_project_id", "project_id"),
        Index("ix_design_reviews_status", "status"),
        Index("ix_design_reviews_type", "review_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    design_document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    ai_suggestions: Mapped[dict | None] = mapped_column(JSONB, default=list)
    compliance_checks: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PredictiveModel(Base):
    __tablename__ = "predictive_models"
    __table_args__ = (
        Index("ix_predictive_models_organization_id", "organization_id"),
        Index("ix_predictive_models_asset_type", "asset_type"),
        Index("ix_predictive_models_status", "status"),
        Index("ix_predictive_models_type", "model_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(500), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="training")
    training_data_count: Mapped[int | None] = mapped_column(Integer)
    accuracy: Mapped[float | None] = mapped_column(Float)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_maintenance_predicted: Mapped[date | None] = mapped_column(Date)
    failure_probability: Mapped[float | None] = mapped_column(Float)
    remaining_life_days: Mapped[int | None] = mapped_column(Integer)
    recommendations: Mapped[dict | None] = mapped_column(JSONB, default=list)
    input_metrics: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
