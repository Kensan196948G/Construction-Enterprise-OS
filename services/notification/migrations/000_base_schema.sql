-- notification スキーマ 基盤 DDL (自動生成 / 冪等)
--
-- 生成元: services/notification/src/models (SQLAlchemy メタデータ)
-- 再生成: python3 scripts/db/generate_base_schema.py notification
--
-- このファイルは models の定義と一致します。既存オブジェクトがある場合は
-- 何もせず、既存データを変更しません。

CREATE SCHEMA IF NOT EXISTS notification;

SET search_path TO notification, public;

DO $$
BEGIN
    IF to_regtype('notification_priority') IS NULL THEN
        CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent');
    END IF;
END
$$;

DO $$
BEGIN
    IF to_regtype('notification_status') IS NULL THEN
        CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'read', 'failed');
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS notification.notification_templates (
	id UUID NOT NULL, 
	code VARCHAR(100) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	channels VARCHAR[] NOT NULL, 
	title_template TEXT NOT NULL, 
	body_template TEXT NOT NULL, 
	priority notification_priority NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code)
);

CREATE TABLE IF NOT EXISTS notification.notifications (
	id BIGSERIAL NOT NULL, 
	template_id UUID, 
	recipient_id UUID NOT NULL, 
	idempotency_key VARCHAR(128), 
	title VARCHAR(500) NOT NULL, 
	body TEXT NOT NULL, 
	metadata JSONB, 
	channels VARCHAR[] NOT NULL, 
	status notification_status NOT NULL, 
	read_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(template_id) REFERENCES notification.notification_templates (id)
);

CREATE INDEX IF NOT EXISTS ix_notification_templates_category ON notification.notification_templates (category);

CREATE UNIQUE INDEX IF NOT EXISTS ix_notification_templates_code ON notification.notification_templates (code);

CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notification.notifications (created_at);

CREATE UNIQUE INDEX IF NOT EXISTS ix_notifications_idempotency_key ON notification.notifications (idempotency_key);

CREATE INDEX IF NOT EXISTS ix_notifications_recipient_id ON notification.notifications (recipient_id);

CREATE INDEX IF NOT EXISTS ix_notifications_status ON notification.notifications (status);
