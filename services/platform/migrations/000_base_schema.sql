-- platform スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/platform/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py platform
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS platform;

SET search_path TO platform, public;

CREATE TABLE IF NOT EXISTS platform.device_groups (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	device_ids UUID[] NOT NULL, 
	group_type VARCHAR(50), 
	parent_group_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_group_id) REFERENCES platform.device_groups (id)
);

CREATE TABLE IF NOT EXISTS platform.iot_dashboards (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	layout JSONB NOT NULL, 
	refresh_interval_seconds INTEGER NOT NULL, 
	is_public BOOLEAN NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS platform.viewer_configs (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(255) NOT NULL, 
	viewer_type VARCHAR(50) NOT NULL, 
	model_ids UUID[] NOT NULL, 
	layer_ids UUID[] NOT NULL, 
	camera_state JSONB NOT NULL, 
	visible_categories TEXT[] NOT NULL, 
	clipping_planes JSONB NOT NULL, 
	theme VARCHAR(20) NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS platform.viewer_scenes (
	id UUID NOT NULL, 
	config_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	camera_state JSONB NOT NULL, 
	annotations JSONB NOT NULL, 
	measurements JSONB NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(config_id) REFERENCES platform.viewer_configs (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_device_groups_org ON platform.device_groups (organization_id);

CREATE INDEX IF NOT EXISTS ix_device_groups_parent ON platform.device_groups (parent_group_id);

CREATE INDEX IF NOT EXISTS ix_device_groups_type ON platform.device_groups (group_type);

CREATE INDEX IF NOT EXISTS ix_iot_dashboards_org ON platform.iot_dashboards (organization_id);

CREATE INDEX IF NOT EXISTS ix_iot_dashboards_project ON platform.iot_dashboards (project_id);

CREATE INDEX IF NOT EXISTS ix_viewer_configs_org ON platform.viewer_configs (organization_id);

CREATE INDEX IF NOT EXISTS ix_viewer_configs_project ON platform.viewer_configs (project_id);

CREATE INDEX IF NOT EXISTS ix_viewer_configs_type ON platform.viewer_configs (viewer_type);

CREATE INDEX IF NOT EXISTS ix_viewer_scenes_config ON platform.viewer_scenes (config_id);
