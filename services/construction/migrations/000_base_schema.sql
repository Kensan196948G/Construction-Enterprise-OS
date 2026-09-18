-- construction スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/construction/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py construction
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS construction;

SET search_path TO construction, public;

CREATE TABLE IF NOT EXISTS construction.wbs_items (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	parent_id UUID, 
	wbs_code VARCHAR(50) NOT NULL, 
	name VARCHAR(500) NOT NULL, 
	description TEXT, 
	level INTEGER NOT NULL, 
	planned_start DATE, 
	planned_end DATE, 
	actual_start DATE, 
	actual_end DATE, 
	planned_cost NUMERIC(15, 2), 
	actual_cost NUMERIC(15, 2), 
	weight_percent NUMERIC(5, 2), 
	progress_percent NUMERIC(5, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	responsible_person UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_id) REFERENCES construction.wbs_items (id)
);

CREATE TABLE IF NOT EXISTS construction.method_statements (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	wbs_item_id UUID, 
	title VARCHAR(500) NOT NULL, 
	document_type VARCHAR(50) NOT NULL, 
	content TEXT, 
	safety_measures TEXT, 
	environmental_measures TEXT, 
	quality_control_points TEXT, 
	required_equipment VARCHAR[], 
	required_materials VARCHAR[], 
	required_labor TEXT, 
	attachments VARCHAR[] NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	approved_by UUID, 
	approved_at TIMESTAMP WITH TIME ZONE, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(wbs_item_id) REFERENCES construction.wbs_items (id)
);

CREATE TABLE IF NOT EXISTS construction.resources (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	wbs_item_id UUID, 
	resource_type VARCHAR(50) NOT NULL, 
	name VARCHAR(500) NOT NULL, 
	specification VARCHAR(500), 
	unit VARCHAR(50), 
	planned_quantity NUMERIC(15, 2), 
	actual_quantity NUMERIC(15, 2), 
	unit_cost NUMERIC(15, 2), 
	total_cost NUMERIC(15, 2), 
	allocation_start DATE, 
	allocation_end DATE, 
	status VARCHAR(20) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(wbs_item_id) REFERENCES construction.wbs_items (id)
);

CREATE TABLE IF NOT EXISTS construction.schedules (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID NOT NULL, 
	wbs_item_id UUID, 
	name VARCHAR(500) NOT NULL, 
	schedule_type VARCHAR(50) NOT NULL, 
	planned_start DATE NOT NULL, 
	planned_end DATE NOT NULL, 
	actual_start DATE, 
	actual_end DATE, 
	duration_days INTEGER, 
	predecessor_ids UUID[] NOT NULL, 
	successor_ids UUID[] NOT NULL, 
	float_days INTEGER, 
	critical_path BOOLEAN NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	progress_percent NUMERIC(5, 2) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(wbs_item_id) REFERENCES construction.wbs_items (id)
);

CREATE INDEX IF NOT EXISTS ix_wbs_items_organization_id ON construction.wbs_items (organization_id);

CREATE INDEX IF NOT EXISTS ix_wbs_items_parent_id ON construction.wbs_items (parent_id);

CREATE INDEX IF NOT EXISTS ix_wbs_items_project_id ON construction.wbs_items (project_id);

CREATE INDEX IF NOT EXISTS ix_wbs_items_status ON construction.wbs_items (status);

CREATE INDEX IF NOT EXISTS ix_method_statements_organization_id ON construction.method_statements (organization_id);

CREATE INDEX IF NOT EXISTS ix_method_statements_project_id ON construction.method_statements (project_id);

CREATE INDEX IF NOT EXISTS ix_method_statements_status ON construction.method_statements (status);

CREATE INDEX IF NOT EXISTS ix_method_statements_wbs_item_id ON construction.method_statements (wbs_item_id);

CREATE INDEX IF NOT EXISTS ix_resources_organization_id ON construction.resources (organization_id);

CREATE INDEX IF NOT EXISTS ix_resources_project_id ON construction.resources (project_id);

CREATE INDEX IF NOT EXISTS ix_resources_status ON construction.resources (status);

CREATE INDEX IF NOT EXISTS ix_resources_wbs_item_id ON construction.resources (wbs_item_id);

CREATE INDEX IF NOT EXISTS ix_schedules_organization_id ON construction.schedules (organization_id);

CREATE INDEX IF NOT EXISTS ix_schedules_project_id ON construction.schedules (project_id);

CREATE INDEX IF NOT EXISTS ix_schedules_status ON construction.schedules (status);

CREATE INDEX IF NOT EXISTS ix_schedules_wbs_item_id ON construction.schedules (wbs_item_id);
