"""GIS関連 SQLAlchemy モデル"""

import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import Date, DateTime, Double, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ConstructionSite(Base):
    __tablename__ = "construction_sites"
    __table_args__ = (
        Index("ix_construction_sites_location", "location", postgresql_using="gist"),
        Index("ix_construction_sites_work_area", "work_area", postgresql_using="gist"),
        Index("ix_construction_sites_org", "organization_id"),
        Index("ix_construction_sites_status", "status"),
        Index("ix_construction_sites_type", "site_type"),
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
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    site_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    work_area: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False), nullable=True
    )
    site_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    elevation: Mapped[float | None] = mapped_column(Double, nullable=True)
    area_sqm: Mapped[float | None] = mapped_column(Double, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    __table_args__ = (
        Index("ix_infrastructure_location", "location", postgresql_using="gist"),
        Index("ix_infrastructure_org", "organization_id"),
        Index("ix_infrastructure_type", "infra_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    infra_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    line_geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=False),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(20), default="active")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class HazardZone(Base):
    __tablename__ = "hazard_zones"
    __table_args__ = (
        Index("ix_hazard_zones_zone_area", "zone_area", postgresql_using="gist"),
        Index("ix_hazard_zones_org", "organization_id"),
        Index("ix_hazard_zones_type", "hazard_type"),
        Index("ix_hazard_zones_risk", "risk_level"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    hazard_type: Mapped[str] = mapped_column(String(50), nullable=False)
    zone_area: Mapped[str] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DroneFlight(Base):
    __tablename__ = "drone_flights"
    __table_args__ = (
        Index("ix_drone_flights_flight_path", "flight_path", postgresql_using="gist"),
        Index("ix_drone_flights_org", "organization_id"),
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
    drone_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    flight_path: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=False),
        nullable=True,
    )
    waypoints: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="MULTIPOINT", srid=4326, spatial_index=False),
        nullable=True,
    )
    flight_area: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=True,
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_altitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
