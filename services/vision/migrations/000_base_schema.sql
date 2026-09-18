-- vision スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/vision/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py vision
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS vision;

SET search_path TO vision, public;

CREATE TABLE IF NOT EXISTS vision.image_analyses (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	file_key VARCHAR(1000) NOT NULL, 
	analysis_type VARCHAR(50) NOT NULL, 
	results JSONB NOT NULL, 
	confidence FLOAT, 
	processing_time_ms INTEGER, 
	model_used VARCHAR(100), 
	status VARCHAR(20) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS vision.ocr_results (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	document_id UUID, 
	file_key VARCHAR(1000), 
	language VARCHAR(10) NOT NULL, 
	extracted_text TEXT NOT NULL, 
	confidence FLOAT, 
	page_count INTEGER, 
	processing_time_ms INTEGER, 
	entities JSONB NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	error_message TEXT, 
	processed_by VARCHAR(100), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS vision.vector_indices (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	collection_name VARCHAR(255) NOT NULL, 
	dimension INTEGER NOT NULL, 
	index_type VARCHAR(50) NOT NULL, 
	metric VARCHAR(20) NOT NULL, 
	document_count INTEGER NOT NULL, 
	total_vectors INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (organization_id, collection_name)
);
