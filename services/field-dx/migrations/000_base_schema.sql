-- field スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/field-dx/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py field-dx
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS field;

SET search_path TO field, public;

CREATE TABLE IF NOT EXISTS field.daily_reports (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	site_id UUID, 
	report_date DATE NOT NULL, 
	weather VARCHAR(20), 
	temperature FLOAT, 
	work_description TEXT NOT NULL, 
	work_results TEXT, 
	worker_count INTEGER, 
	equipment_used VARCHAR[], 
	materials_used VARCHAR[], 
	issues TEXT, 
	next_plan TEXT, 
	status VARCHAR(20) NOT NULL, 
	created_by UUID NOT NULL, 
	approved_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS field.progress_records (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	activity_name VARCHAR(500) NOT NULL, 
	activity_code VARCHAR(100), 
	planned_quantity FLOAT, 
	actual_quantity FLOAT, 
	unit VARCHAR(50), 
	planned_start DATE, 
	planned_end DATE, 
	actual_start DATE, 
	actual_end DATE, 
	progress_percent FLOAT, 
	status VARCHAR(20) NOT NULL, 
	notes TEXT, 
	recorded_by UUID NOT NULL, 
	recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS field.quality_checks (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	check_item VARCHAR(500) NOT NULL, 
	check_type VARCHAR(50) NOT NULL, 
	standard_value VARCHAR(255), 
	measured_value VARCHAR(255), 
	is_conforming BOOLEAN, 
	check_date DATE NOT NULL, 
	location VARCHAR(500), 
	inspector_id UUID NOT NULL, 
	notes TEXT, 
	status VARCHAR(20) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_daily_reports_organization_id ON field.daily_reports (organization_id);

CREATE INDEX IF NOT EXISTS ix_daily_reports_project_id ON field.daily_reports (project_id);

CREATE INDEX IF NOT EXISTS ix_daily_reports_report_date ON field.daily_reports (report_date);

CREATE INDEX IF NOT EXISTS ix_daily_reports_status ON field.daily_reports (status);

CREATE INDEX IF NOT EXISTS ix_progress_records_organization_id ON field.progress_records (organization_id);

CREATE INDEX IF NOT EXISTS ix_progress_records_project_id ON field.progress_records (project_id);

CREATE INDEX IF NOT EXISTS ix_progress_records_status ON field.progress_records (status);

CREATE INDEX IF NOT EXISTS ix_quality_checks_check_date ON field.quality_checks (check_date);

CREATE INDEX IF NOT EXISTS ix_quality_checks_organization_id ON field.quality_checks (organization_id);

CREATE INDEX IF NOT EXISTS ix_quality_checks_project_id ON field.quality_checks (project_id);

CREATE INDEX IF NOT EXISTS ix_quality_checks_status ON field.quality_checks (status);
