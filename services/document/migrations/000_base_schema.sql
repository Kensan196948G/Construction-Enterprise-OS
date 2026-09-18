-- document スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/document/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py document
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS document;

SET search_path TO document, public;

DO $$
BEGIN
    IF to_regtype('document.document_type') IS NULL THEN
        CREATE TYPE document.document_type AS ENUM ('pdf', 'cad', 'bim', 'photo', 'video', 'spreadsheet', 'other');
    END IF;
END
$$;

DO $$
BEGIN
    IF to_regtype('document.document_status') IS NULL THEN
        CREATE TYPE document.document_status AS ENUM ('draft', 'under_review', 'approved', 'rejected', 'obsolete', 'deleted');
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS document.documents (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	project_id UUID, 
	name VARCHAR(500) NOT NULL, 
	description TEXT, 
	document_type document.document_type NOT NULL, 
	status document.document_status NOT NULL, 
	current_version INTEGER NOT NULL, 
	file_name VARCHAR(500) NOT NULL, 
	file_size BIGINT NOT NULL, 
	mime_type VARCHAR(255) NOT NULL, 
	storage_key VARCHAR(1000) NOT NULL, 
	tags VARCHAR[] DEFAULT '{}' NOT NULL, 
	metadata JSONB, 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	canonical_stored_at TIMESTAMP WITH TIME ZONE, 
	canonical_path VARCHAR(1000), 
	work_area_receipt_no VARCHAR(30), 
	work_area_stored_at TIMESTAMP WITH TIME ZONE, 
	work_area_path VARCHAR(1000), 
	storage_backend VARCHAR(20), 
	storage_error TEXT, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS document.document_versions (
	id UUID NOT NULL, 
	document_id UUID NOT NULL, 
	version_number INTEGER NOT NULL, 
	file_name VARCHAR(500) NOT NULL, 
	file_size BIGINT NOT NULL, 
	mime_type VARCHAR(255) NOT NULL, 
	storage_key VARCHAR(1000) NOT NULL, 
	change_description TEXT, 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(document_id) REFERENCES document.documents (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_documents_created_at ON document.documents (created_at);

CREATE INDEX IF NOT EXISTS ix_documents_document_type ON document.documents (document_type);

CREATE INDEX IF NOT EXISTS ix_documents_organization_id ON document.documents (organization_id);

CREATE INDEX IF NOT EXISTS ix_documents_project_id ON document.documents (project_id);

CREATE INDEX IF NOT EXISTS ix_documents_status ON document.documents (status);

CREATE INDEX IF NOT EXISTS ix_document_versions_document_id ON document.document_versions (document_id);

CREATE UNIQUE INDEX IF NOT EXISTS ix_document_versions_document_id_version ON document.document_versions (document_id, version_number);
