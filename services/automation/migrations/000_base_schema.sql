-- automation スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/automation/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py automation
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS automation;

SET search_path TO automation, public;

CREATE TABLE IF NOT EXISTS automation.automation_rules (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	trigger_type VARCHAR(50) NOT NULL, 
	condition JSONB NOT NULL, 
	action JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_by UUID, 
	last_triggered TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS automation.scheduled_task_runs (
	id UUID NOT NULL, 
	task_id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	output_data JSONB NOT NULL, 
	error_message TEXT, 
	started_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	duration_ms INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS automation.scheduled_tasks (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	cron_expression VARCHAR(100) NOT NULL, 
	action_type VARCHAR(50) NOT NULL, 
	action_config JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_by UUID, 
	last_run TIMESTAMP WITH TIME ZONE, 
	next_run TIMESTAMP WITH TIME ZONE, 
	last_status VARCHAR(20), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS automation.triggers (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	event_type VARCHAR(100) NOT NULL, 
	filter_conditions JSONB NOT NULL, 
	action_config JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_by UUID, 
	last_triggered TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
