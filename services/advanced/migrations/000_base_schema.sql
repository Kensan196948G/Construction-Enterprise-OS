-- advanced スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/advanced/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py advanced
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS advanced;

SET search_path TO advanced, public;

CREATE TABLE IF NOT EXISTS advanced.design_reviews (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	design_document_id UUID, 
	review_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	ai_suggestions JSONB, 
	compliance_checks JSONB, 
	reviewer_id UUID, 
	reviewed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS advanced.inspection_records (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	asset_name VARCHAR(500) NOT NULL, 
	asset_type VARCHAR(50) NOT NULL, 
	inspection_method VARCHAR(50), 
	ai_model_used VARCHAR(100), 
	defect_type VARCHAR(50), 
	severity VARCHAR(20), 
	confidence FLOAT, 
	defect_count INTEGER, 
	location TEXT, 
	image_keys VARCHAR[], 
	ai_analysis JSONB, 
	inspector_id UUID, 
	inspection_date DATE NOT NULL, 
	requires_action BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS advanced.marine_construction (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(500) NOT NULL, 
	construction_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	water_depth FLOAT, 
	tide_info JSONB, 
	wave_condition JSONB, 
	equipment_deployed VARCHAR[], 
	material_volume NUMERIC(15, 2), 
	progress_percent NUMERIC(5, 2), 
	location TEXT, 
	start_date DATE, 
	end_date DATE, 
	supervisor_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS advanced.predictive_models (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	asset_name VARCHAR(500) NOT NULL, 
	asset_type VARCHAR(50) NOT NULL, 
	model_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	training_data_count INTEGER, 
	accuracy FLOAT, 
	last_trained_at TIMESTAMP WITH TIME ZONE, 
	next_maintenance_predicted DATE, 
	failure_probability FLOAT, 
	remaining_life_days INTEGER, 
	recommendations JSONB, 
	input_metrics JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_design_reviews_organization_id ON advanced.design_reviews (organization_id);

CREATE INDEX IF NOT EXISTS ix_design_reviews_project_id ON advanced.design_reviews (project_id);

CREATE INDEX IF NOT EXISTS ix_design_reviews_status ON advanced.design_reviews (status);

CREATE INDEX IF NOT EXISTS ix_design_reviews_type ON advanced.design_reviews (review_type);

CREATE INDEX IF NOT EXISTS ix_inspection_records_asset_type ON advanced.inspection_records (asset_type);

CREATE INDEX IF NOT EXISTS ix_inspection_records_inspection_date ON advanced.inspection_records (inspection_date);

CREATE INDEX IF NOT EXISTS ix_inspection_records_organization_id ON advanced.inspection_records (organization_id);

CREATE INDEX IF NOT EXISTS ix_inspection_records_severity ON advanced.inspection_records (severity);

CREATE INDEX IF NOT EXISTS ix_marine_construction_organization_id ON advanced.marine_construction (organization_id);

CREATE INDEX IF NOT EXISTS ix_marine_construction_project_id ON advanced.marine_construction (project_id);

CREATE INDEX IF NOT EXISTS ix_marine_construction_status ON advanced.marine_construction (status);

CREATE INDEX IF NOT EXISTS ix_marine_construction_type ON advanced.marine_construction (construction_type);

CREATE INDEX IF NOT EXISTS ix_predictive_models_asset_type ON advanced.predictive_models (asset_type);

CREATE INDEX IF NOT EXISTS ix_predictive_models_organization_id ON advanced.predictive_models (organization_id);

CREATE INDEX IF NOT EXISTS ix_predictive_models_status ON advanced.predictive_models (status);

CREATE INDEX IF NOT EXISTS ix_predictive_models_type ON advanced.predictive_models (model_type);
