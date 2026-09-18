-- safety スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/safety/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py safety
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS safety;

SET search_path TO safety, public;

CREATE TABLE IF NOT EXISTS safety.hazard_reports (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	site_id UUID, 
	title VARCHAR(500) NOT NULL, 
	description TEXT NOT NULL, 
	hazard_type VARCHAR(50) NOT NULL, 
	risk_level VARCHAR(20) NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	location VARCHAR(500), 
	reported_by UUID NOT NULL, 
	assigned_to UUID, 
	mitigation TEXT, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS safety.safety_incidents (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	site_id UUID, 
	title VARCHAR(500) NOT NULL, 
	description TEXT NOT NULL, 
	incident_type VARCHAR(50) NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	incident_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	location VARCHAR(500), 
	injured_count INTEGER NOT NULL, 
	fatality_count INTEGER NOT NULL, 
	root_cause TEXT, 
	corrective_actions TEXT, 
	reported_by UUID NOT NULL, 
	investigated_by UUID, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	is_osha_reportable BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS safety.safety_inspections (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	site_id UUID, 
	title VARCHAR(500) NOT NULL, 
	inspection_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	inspector_id UUID NOT NULL, 
	inspection_date DATE, 
	location VARCHAR(500), 
	findings TEXT, 
	corrective_actions TEXT, 
	score INTEGER CHECK (score >= 0 AND score <= 100), 
	is_safe BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);
