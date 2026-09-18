-- gis スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/gis/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py gis
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS gis;

SET search_path TO gis, public;

CREATE TABLE IF NOT EXISTS gis.construction_sites (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(500) NOT NULL, 
	site_code VARCHAR(100), 
	location geometry(POINT,4326) NOT NULL, 
	work_area geometry(POLYGON,4326), 
	site_type VARCHAR(50), 
	status VARCHAR(20) NOT NULL, 
	address VARCHAR(500), 
	elevation DOUBLE PRECISION, 
	area_sqm DOUBLE PRECISION, 
	start_date DATE, 
	end_date DATE, 
	metadata JSONB, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS gis.drone_flights (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	drone_name VARCHAR(200), 
	flight_path geometry(LINESTRING,4326), 
	waypoints geometry(MULTIPOINT,4326), 
	flight_area geometry(POLYGON,4326), 
	start_time TIMESTAMP WITH TIME ZONE, 
	end_time TIMESTAMP WITH TIME ZONE, 
	max_altitude DOUBLE PRECISION, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS gis.hazard_zones (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(500) NOT NULL, 
	hazard_type VARCHAR(50) NOT NULL, 
	zone_area geometry(POLYGON,4326) NOT NULL, 
	risk_level VARCHAR(20) NOT NULL, 
	description TEXT, 
	valid_from DATE, 
	valid_to DATE, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS gis.infrastructure (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(500) NOT NULL, 
	infra_type VARCHAR(50) NOT NULL, 
	location geometry(POINT,4326) NOT NULL, 
	line_geom geometry(LINESTRING,4326), 
	status VARCHAR(20) NOT NULL, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_construction_sites_location ON gis.construction_sites USING gist (location);

CREATE INDEX IF NOT EXISTS ix_construction_sites_org ON gis.construction_sites (organization_id);

CREATE INDEX IF NOT EXISTS ix_construction_sites_status ON gis.construction_sites (status);

CREATE INDEX IF NOT EXISTS ix_construction_sites_type ON gis.construction_sites (site_type);

CREATE INDEX IF NOT EXISTS ix_construction_sites_work_area ON gis.construction_sites USING gist (work_area);

CREATE INDEX IF NOT EXISTS ix_drone_flights_flight_path ON gis.drone_flights USING gist (flight_path);

CREATE INDEX IF NOT EXISTS ix_drone_flights_org ON gis.drone_flights (organization_id);

CREATE INDEX IF NOT EXISTS ix_hazard_zones_org ON gis.hazard_zones (organization_id);

CREATE INDEX IF NOT EXISTS ix_hazard_zones_risk ON gis.hazard_zones (risk_level);

CREATE INDEX IF NOT EXISTS ix_hazard_zones_type ON gis.hazard_zones (hazard_type);

CREATE INDEX IF NOT EXISTS ix_hazard_zones_zone_area ON gis.hazard_zones USING gist (zone_area);

CREATE INDEX IF NOT EXISTS ix_infrastructure_location ON gis.infrastructure USING gist (location);

CREATE INDEX IF NOT EXISTS ix_infrastructure_org ON gis.infrastructure (organization_id);

CREATE INDEX IF NOT EXISTS ix_infrastructure_type ON gis.infrastructure (infra_type);
