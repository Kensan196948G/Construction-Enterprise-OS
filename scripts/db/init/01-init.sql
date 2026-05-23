-- CEO-OS データベース初期化
-- Docker Compose起動時に自動実行されます

-- 認証スキーマ
CREATE SCHEMA IF NOT EXISTS auth;
-- マスターデータスキーマ
CREATE SCHEMA IF NOT EXISTS master;
-- 工事管理スキーマ
CREATE SCHEMA IF NOT EXISTS project;
-- 承認ワークフロースキーマ
CREATE SCHEMA IF NOT EXISTS workflow;
-- 文書管理スキーマ
CREATE SCHEMA IF NOT EXISTS document;
-- 経営管理スキーマ
CREATE SCHEMA IF NOT EXISTS erp;
-- 安全管理スキーマ
CREATE SCHEMA IF NOT EXISTS safety;
-- 品質管理スキーマ
CREATE SCHEMA IF NOT EXISTS quality;
-- 協力会社スキーマ
CREATE SCHEMA IF NOT EXISTS partner;
-- 監査ログスキーマ
CREATE SCHEMA IF NOT EXISTS audit;
-- IoT スキーマ
CREATE SCHEMA IF NOT EXISTS iot;

-- デフォルト組織（開発用）
INSERT INTO auth.organizations (id, name, type, status)
VALUES
  (gen_random_uuid(), 'CEO-OS 本社', 'company', 'active'),
  (gen_random_uuid(), '建設事業部', 'department', 'active'),
  (gen_random_uuid(), '土木事業部', 'department', 'active'),
  (gen_random_uuid(), '東京現場 A', 'site', 'active'),
  (gen_random_uuid(), '大阪現場 B', 'site', 'active');

-- デフォルト権限（開発用）
INSERT INTO auth.permissions (id, resource, action, description) VALUES
  (gen_random_uuid(), 'users', 'read', 'ユーザー情報の閲覧'),
  (gen_random_uuid(), 'users', 'create', 'ユーザーの作成'),
  (gen_random_uuid(), 'users', 'update', 'ユーザー情報の更新'),
  (gen_random_uuid(), 'users', 'delete', 'ユーザーの削除'),
  (gen_random_uuid(), 'roles', 'read', 'ロール情報の閲覧'),
  (gen_random_uuid(), 'roles', 'create', 'ロールの作成'),
  (gen_random_uuid(), 'roles', 'update', 'ロール情報の更新'),
  (gen_random_uuid(), 'roles', 'delete', 'ロールの削除'),
  (gen_random_uuid(), 'documents', 'read', '文書の閲覧'),
  (gen_random_uuid(), 'documents', 'create', '文書の作成'),
  (gen_random_uuid(), 'documents', 'approve', '文書の承認'),
  (gen_random_uuid(), 'documents', 'delete', '文書の削除'),
  (gen_random_uuid(), 'projects', 'read', '工事情報の閲覧'),
  (gen_random_uuid(), 'projects', 'create', '工事の作成'),
  (gen_random_uuid(), 'projects', 'update', '工事情報の更新'),
  (gen_random_uuid(), 'iot', 'read', 'IoTデータの閲覧'),
  (gen_random_uuid(), 'iot', 'ingest', 'IoTデータの送信'),
  (gen_random_uuid(), 'gis', 'read', 'GISデータの閲覧'),
  (gen_random_uuid(), 'bim', 'read', 'BIMデータの閲覧'),
  (gen_random_uuid(), 'workflow', 'approve', 'ワークフロー承認');
