-- ai スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/ai/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py ai
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS ai;

SET search_path TO ai, public;

CREATE TABLE IF NOT EXISTS ai.conversations (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR(500), 
	category VARCHAR(50), 
	status VARCHAR(20) NOT NULL, 
	context_type VARCHAR(50), 
	context_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ai.embeddings (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	source_type VARCHAR(50) NOT NULL, 
	source_id UUID NOT NULL, 
	chunk_index INTEGER NOT NULL, 
	content TEXT NOT NULL, 
	embedding VECTOR(1536), 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ai.knowledge_base (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	content TEXT NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	tags VARCHAR[] DEFAULT '{}' NOT NULL, 
	source_url VARCHAR(2048), 
	is_published BOOLEAN DEFAULT false NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ai.prompt_templates (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	category VARCHAR(50) NOT NULL, 
	system_prompt TEXT NOT NULL, 
	user_prompt_template TEXT NOT NULL, 
	model VARCHAR(50) NOT NULL, 
	temperature DOUBLE PRECISION NOT NULL, 
	max_tokens INTEGER NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ai.messages (
	id SERIAL NOT NULL, 
	conversation_id UUID NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	token_count INTEGER, 
	metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(conversation_id) REFERENCES ai.conversations (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_conversations_organization_id ON ai.conversations (organization_id);

CREATE INDEX IF NOT EXISTS ix_conversations_status ON ai.conversations (status);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON ai.conversations (user_id);

CREATE INDEX IF NOT EXISTS ix_embeddings_organization_id ON ai.embeddings (organization_id);

CREATE INDEX IF NOT EXISTS ix_embeddings_source_type_source_id ON ai.embeddings (source_type, source_id);

CREATE INDEX IF NOT EXISTS ix_knowledge_base_category ON ai.knowledge_base (category);

CREATE INDEX IF NOT EXISTS ix_knowledge_base_organization_id ON ai.knowledge_base (organization_id);

CREATE INDEX IF NOT EXISTS ix_prompt_templates_category ON ai.prompt_templates (category);

CREATE INDEX IF NOT EXISTS ix_prompt_templates_is_active ON ai.prompt_templates (is_active);

CREATE INDEX IF NOT EXISTS ix_prompt_templates_organization_id ON ai.prompt_templates (organization_id);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON ai.messages (conversation_id);
