-- analytics スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/analytics/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py analytics
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS analytics;

SET search_path TO analytics, public;

CREATE TABLE IF NOT EXISTS analytics.analytics_reports (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	report_type VARCHAR(50) NOT NULL, 
	query_config JSONB NOT NULL, 
	schedule VARCHAR(100), 
	status VARCHAR(20) NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS analytics.data_sources (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	source_type VARCHAR(50) NOT NULL, 
	connection_config JSONB NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	description TEXT, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS analytics.data_pipelines (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	source_id UUID, 
	target_id UUID, 
	transform_logic JSONB NOT NULL, 
	schedule VARCHAR(100), 
	status VARCHAR(20) NOT NULL, 
	last_run TIMESTAMP WITH TIME ZONE, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(source_id) REFERENCES analytics.data_sources (id), 
	FOREIGN KEY(target_id) REFERENCES analytics.data_sources (id)
);

CREATE INDEX IF NOT EXISTS ix_analytics_reports_organization_id ON analytics.analytics_reports (organization_id);

CREATE INDEX IF NOT EXISTS ix_analytics_reports_report_type ON analytics.analytics_reports (report_type);

CREATE INDEX IF NOT EXISTS ix_analytics_reports_status ON analytics.analytics_reports (status);

CREATE INDEX IF NOT EXISTS ix_data_sources_organization_id ON analytics.data_sources (organization_id);

CREATE INDEX IF NOT EXISTS ix_data_sources_source_type ON analytics.data_sources (source_type);

CREATE INDEX IF NOT EXISTS ix_data_sources_status ON analytics.data_sources (status);

CREATE INDEX IF NOT EXISTS ix_data_pipelines_organization_id ON analytics.data_pipelines (organization_id);

CREATE INDEX IF NOT EXISTS ix_data_pipelines_source_id ON analytics.data_pipelines (source_id);

CREATE INDEX IF NOT EXISTS ix_data_pipelines_status ON analytics.data_pipelines (status);

CREATE INDEX IF NOT EXISTS ix_data_pipelines_target_id ON analytics.data_pipelines (target_id);
