"""Autonomous データモデル (AutonomousAgent, DigitalTwin, Task, Simulation)"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AutonomousAgent(Base):
    __tablename__ = "autonomous_agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="idle")
    target_resource: Mapped[str | None] = mapped_column(String(255))
    config: Mapped[dict] = mapped_column("config", JSONB, default=dict)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tasks: Mapped[list["AutonomousTask"]] = relationship(
        "AutonomousTask", back_populates="agent", cascade="all, delete-orphan"
    )


class DigitalTwin(Base):
    __tablename__ = "digital_twins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    twin_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="initializing")
    bim_model_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    iot_device_ids: Mapped[list] = mapped_column("iot_device_ids", ARRAY(UUID), default=list)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sync_interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    data_sources: Mapped[dict] = mapped_column("data_sources", JSONB, default=dict)
    current_state: Mapped[dict] = mapped_column("current_state", JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tasks: Mapped[list["AutonomousTask"]] = relationship(
        "AutonomousTask", back_populates="digital_twin", cascade="all, delete-orphan"
    )
    simulations: Mapped[list["ConstructionSimulation"]] = relationship(
        "ConstructionSimulation", back_populates="digital_twin", cascade="all, delete-orphan"
    )


class AutonomousTask(Base):
    __tablename__ = "autonomous_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("autonomous.autonomous_agents.id")
    )
    digital_twin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("autonomous.digital_twins.id")
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    input_data: Mapped[dict | None] = mapped_column("input_data", JSONB)
    output_data: Mapped[dict | None] = mapped_column("output_data", JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    agent: Mapped["AutonomousAgent"] = relationship("AutonomousAgent", back_populates="tasks")
    digital_twin: Mapped["DigitalTwin"] = relationship("DigitalTwin", back_populates="tasks")


class ConstructionSimulation(Base):
    __tablename__ = "construction_simulations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    digital_twin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("autonomous.digital_twins.id")
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    simulation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    parameters: Mapped[dict] = mapped_column("parameters", JSONB, default=dict)
    results: Mapped[dict] = mapped_column("results", JSONB, default=dict)
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    digital_twin: Mapped["DigitalTwin"] = relationship("DigitalTwin", back_populates="simulations")
