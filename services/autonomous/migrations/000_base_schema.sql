-- autonomous スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/autonomous/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py autonomous
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS autonomous;

SET search_path TO autonomous, public;

CREATE TABLE IF NOT EXISTS autonomous.autonomous_agents (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	agent_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	target_resource VARCHAR(255), 
	config JSONB NOT NULL, 
	last_run_at TIMESTAMP WITH TIME ZONE, 
	run_count INTEGER NOT NULL, 
	error_count INTEGER NOT NULL, 
	is_enabled BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS autonomous.autonomous_controls (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	target_id UUID NOT NULL, 
	target_type VARCHAR(50) NOT NULL, 
	command_type VARCHAR(50) NOT NULL, 
	parameters JSONB NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	issued_by UUID NOT NULL, 
	executed_at TIMESTAMP WITH TIME ZONE, 
	result JSONB, 
	error_message TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS autonomous.digital_twins (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(500) NOT NULL, 
	twin_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	bim_model_id UUID, 
	iot_device_ids UUID[] NOT NULL, 
	last_sync_at TIMESTAMP WITH TIME ZONE, 
	sync_interval_seconds INTEGER NOT NULL, 
	data_sources JSONB NOT NULL, 
	current_state JSONB NOT NULL, 
	metadata JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS autonomous.marine_robotics (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	robot_name VARCHAR(255) NOT NULL, 
	robot_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	mission_type VARCHAR(50), 
	location JSONB, 
	depth_meters FLOAT, 
	battery_level INTEGER, 
	mission_plan JSONB NOT NULL, 
	telemetry JSONB NOT NULL, 
	last_contact TIMESTAMP WITH TIME ZONE, 
	deployed_at TIMESTAMP WITH TIME ZONE, 
	recovered_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS autonomous.autonomous_operations (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	digital_twin_id UUID, 
	name VARCHAR(500) NOT NULL, 
	operation_type VARCHAR(50) NOT NULL, 
	equipment_id UUID, 
	status VARCHAR(20) NOT NULL, 
	plan_data JSONB NOT NULL, 
	execution_log JSONB NOT NULL, 
	progress_percent NUMERIC(5, 2) NOT NULL, 
	safety_status VARCHAR(20) NOT NULL, 
	area JSONB, 
	start_time TIMESTAMP WITH TIME ZONE, 
	end_time TIMESTAMP WITH TIME ZONE, 
	operator_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(digital_twin_id) REFERENCES autonomous.digital_twins (id)
);

CREATE TABLE IF NOT EXISTS autonomous.autonomous_tasks (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	agent_id UUID, 
	digital_twin_id UUID, 
	title VARCHAR(500) NOT NULL, 
	task_type VARCHAR(50) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	input_data JSONB, 
	output_data JSONB, 
	error_message TEXT, 
	started_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	duration_ms INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(agent_id) REFERENCES autonomous.autonomous_agents (id), 
	FOREIGN KEY(digital_twin_id) REFERENCES autonomous.digital_twins (id)
);

CREATE TABLE IF NOT EXISTS autonomous.construction_simulations (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	digital_twin_id UUID, 
	name VARCHAR(500) NOT NULL, 
	simulation_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	parameters JSONB NOT NULL, 
	results JSONB NOT NULL, 
	progress_percent NUMERIC(5, 2) NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(digital_twin_id) REFERENCES autonomous.digital_twins (id)
);
