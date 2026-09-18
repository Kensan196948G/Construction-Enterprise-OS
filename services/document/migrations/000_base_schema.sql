-- Document Service base schema (idempotent).
--
-- このファイルは services/document/src/models/__init__.py の定義と一致する
-- 基盤 DDL です。これまで document スキーマのテーブルを作成する DDL が
-- リポジトリ内に存在せず、実データベースでは手作業で作られた想定になって
-- いました。空のデータベースから再現できるようここに明示します。
--
-- 冪等: 既存オブジェクトがある場合は何もしません。既存データは変更しません。
-- ENUM 型はテーブルと同じ document スキーマに作成します
-- (MetaData(schema="document") と一致させるため)。

CREATE SCHEMA IF NOT EXISTS document;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_type t
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'document' AND t.typname = 'document_type'
    ) THEN
        CREATE TYPE document.document_type AS ENUM (
            'pdf', 'cad', 'bim', 'photo', 'video', 'spreadsheet', 'other'
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_type t
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'document' AND t.typname = 'document_status'
    ) THEN
        CREATE TYPE document.document_status AS ENUM (
            'draft', 'under_review', 'approved', 'rejected', 'obsolete', 'deleted'
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS document.documents (
    id uuid NOT NULL,
    organization_id uuid NOT NULL,
    project_id uuid,
    name character varying(500) NOT NULL,
    description text,
    document_type document.document_type NOT NULL,
    status document.document_status NOT NULL,
    current_version integer NOT NULL,
    file_name character varying(500) NOT NULL,
    file_size bigint NOT NULL,
    mime_type character varying(255) NOT NULL,
    storage_key character varying(1000) NOT NULL,
    tags character varying[] DEFAULT '{}'::character varying[] NOT NULL,
    metadata jsonb,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    canonical_stored_at timestamp with time zone,
    canonical_path character varying(1000),
    work_area_receipt_no character varying(30),
    work_area_stored_at timestamp with time zone,
    work_area_path character varying(1000),
    storage_backend character varying(20),
    storage_error text,
    CONSTRAINT documents_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS document.document_versions (
    id uuid NOT NULL,
    document_id uuid NOT NULL,
    version_number integer NOT NULL,
    file_name character varying(500) NOT NULL,
    file_size bigint NOT NULL,
    mime_type character varying(255) NOT NULL,
    storage_key character varying(1000) NOT NULL,
    change_description text,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT document_versions_pkey PRIMARY KEY (id),
    CONSTRAINT document_versions_document_id_fkey
        FOREIGN KEY (document_id) REFERENCES document.documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_documents_organization_id
    ON document.documents USING btree (organization_id);
CREATE INDEX IF NOT EXISTS ix_documents_project_id
    ON document.documents USING btree (project_id);
CREATE INDEX IF NOT EXISTS ix_documents_document_type
    ON document.documents USING btree (document_type);
CREATE INDEX IF NOT EXISTS ix_documents_status
    ON document.documents USING btree (status);
CREATE INDEX IF NOT EXISTS ix_documents_created_at
    ON document.documents USING btree (created_at);
CREATE INDEX IF NOT EXISTS ix_document_versions_document_id
    ON document.document_versions USING btree (document_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_document_versions_document_id_version
    ON document.document_versions USING btree (document_id, version_number);
