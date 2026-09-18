-- iot スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/iot/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py iot
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS iot;

SET search_path TO iot, public;

CREATE TABLE IF NOT EXISTS iot.alert_rules (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	device_id UUID, 
	sensor_id UUID, 
	name VARCHAR(255) NOT NULL, 
	metric_name VARCHAR(100) NOT NULL, 
	condition VARCHAR(20) NOT NULL, 
	threshold DOUBLE PRECISION NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	cooldown_minutes INTEGER NOT NULL, 
	notification_channels VARCHAR[], 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS iot.devices (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	site_id UUID, 
	name VARCHAR(255) NOT NULL, 
	device_type VARCHAR(50) NOT NULL, 
	serial_number VARCHAR(100), 
	firmware_version VARCHAR(50), 
	status VARCHAR(20) NOT NULL, 
	battery_level INTEGER, 
	location TEXT, 
	metadata JSONB, 
	last_seen_at TIMESTAMP WITH TIME ZONE, 
	registered_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS iot.telemetry (
	id BIGSERIAL NOT NULL, 
	device_id UUID NOT NULL, 
	sensor_id UUID, 
	metric_name VARCHAR(100) NOT NULL, 
	value DOUBLE PRECISION NOT NULL, 
	unit VARCHAR(50), 
	timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	metadata JSONB, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS iot.alert_history (
	id BIGSERIAL NOT NULL, 
	rule_id UUID, 
	device_id UUID NOT NULL, 
	sensor_id UUID, 
	metric_name VARCHAR(100) NOT NULL, 
	current_value DOUBLE PRECISION NOT NULL, 
	threshold DOUBLE PRECISION NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	message TEXT NOT NULL, 
	acknowledged_by UUID, 
	acknowledged_at TIMESTAMP WITH TIME ZONE, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(rule_id) REFERENCES iot.alert_rules (id)
);

CREATE TABLE IF NOT EXISTS iot.sensors (
	id UUID NOT NULL, 
	device_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	sensor_type VARCHAR(50) NOT NULL, 
	unit VARCHAR(50), 
	min_value DOUBLE PRECISION, 
	max_value DOUBLE PRECISION, 
	is_active BOOLEAN NOT NULL, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(device_id) REFERENCES iot.devices (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_alert_rules_device_id ON iot.alert_rules (device_id);

CREATE INDEX IF NOT EXISTS ix_alert_rules_organization_id ON iot.alert_rules (organization_id);

CREATE INDEX IF NOT EXISTS ix_devices_device_type ON iot.devices (device_type);

CREATE INDEX IF NOT EXISTS ix_devices_organization_id ON iot.devices (organization_id);

CREATE INDEX IF NOT EXISTS ix_devices_project_id ON iot.devices (project_id);

CREATE INDEX IF NOT EXISTS ix_devices_status ON iot.devices (status);

CREATE INDEX IF NOT EXISTS ix_telemetry_device_id_timestamp ON iot.telemetry (device_id, timestamp);

CREATE INDEX IF NOT EXISTS ix_telemetry_metric_name ON iot.telemetry (metric_name);

CREATE INDEX IF NOT EXISTS ix_alert_history_created_at ON iot.alert_history (created_at);

CREATE INDEX IF NOT EXISTS ix_alert_history_device_id ON iot.alert_history (device_id);

CREATE INDEX IF NOT EXISTS ix_alert_history_severity ON iot.alert_history (severity);

CREATE INDEX IF NOT EXISTS ix_sensors_device_id ON iot.sensors (device_id);
