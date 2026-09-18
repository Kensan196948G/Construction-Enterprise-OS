-- security スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/security/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py security
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS security;

SET search_path TO security, public;

CREATE TABLE IF NOT EXISTS security.security_audits (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	audit_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	findings TEXT, 
	recommendations TEXT, 
	auditor VARCHAR(255), 
	scheduled_date DATE, 
	completed_date DATE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS security.security_incidents (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	severity VARCHAR(20) NOT NULL, 
	incident_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	source_ip INET, 
	affected_systems TEXT[], 
	detected_by VARCHAR(255), 
	assigned_to UUID, 
	resolution TEXT, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS security.security_policies (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	category VARCHAR(50) NOT NULL, 
	content TEXT NOT NULL, 
	version INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	effective_date DATE, 
	review_date DATE, 
	approved_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS security.vulnerabilities (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	severity VARCHAR(20) NOT NULL, 
	cve_id VARCHAR(50), 
	cvss_score DOUBLE PRECISION, 
	affected_component VARCHAR(500), 
	status VARCHAR(20) NOT NULL, 
	remediation TEXT, 
	discovered_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	fixed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS security.incident_updates (
	id BIGSERIAL NOT NULL, 
	incident_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	update_type VARCHAR(50) NOT NULL, 
	content TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(incident_id) REFERENCES security.security_incidents (id) ON DELETE CASCADE
);
