-- maintenance スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/maintenance/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py maintenance
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS maintenance;

SET search_path TO maintenance, public;

CREATE TABLE IF NOT EXISTS maintenance.disaster_reports (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	title VARCHAR(500) NOT NULL, 
	disaster_type VARCHAR(50) NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	occurred_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	location VARCHAR(500), 
	description TEXT NOT NULL, 
	damage_assessment TEXT, 
	estimated_cost NUMERIC(15, 2), 
	casualties INTEGER NOT NULL, 
	evacuation_required BOOLEAN NOT NULL, 
	reported_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS maintenance.inspection_schedules (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	asset_name VARCHAR(500) NOT NULL, 
	asset_type VARCHAR(50) NOT NULL, 
	inspection_type VARCHAR(50) NOT NULL, 
	frequency VARCHAR(20) NOT NULL, 
	last_inspection_date DATE, 
	next_inspection_date DATE NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	inspector VARCHAR(255), 
	checklist TEXT, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS maintenance.maintenance_records (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	asset_name VARCHAR(500) NOT NULL, 
	asset_type VARCHAR(50) NOT NULL, 
	maintenance_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	description TEXT NOT NULL, 
	work_performed TEXT, 
	cost NUMERIC(15, 2), 
	contractor VARCHAR(255), 
	scheduled_date DATE, 
	completed_date DATE, 
	next_maintenance_date DATE, 
	location VARCHAR(500), 
	performed_by UUID, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS maintenance.recovery_plans (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	disaster_report_id UUID, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	priority VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	estimated_duration_days INTEGER, 
	estimated_cost NUMERIC(15, 2), 
	actual_cost NUMERIC(15, 2), 
	start_date DATE, 
	completed_date DATE, 
	contractor VARCHAR(255), 
	resources_needed TEXT, 
	progress_percent NUMERIC(5, 2), 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);
