# 統合認証基盤 (Auth Platform) 詳細設計

## 1. 責務

Construction-Enterprise-OSの全サービス・全ユーザー・全デバイスに対する統合認証・認可を提供する「OSのログイン機能」。

## 2. 機能要件

### 2.1 認証方式
| 機能 | 優先度 | 説明 |
|---|---|---|
| ID/Password + MFA | P0 | 基本認証。TOTPベースの多要素認証 |
| SSO (SAML/OIDC) | P0 | 全サービス共通のシングルサインオン |
| Entra ID連携 | P1 | Azure AD / Microsoft 365連携 |
| Active Directory連携 | P1 | オンプレミスAD連携 |
| 協力会社ID | P0 | 外部ユーザー向けフェデレーション認証 |
| デバイス認証 | P1 | 現場端末・IoTデバイスの証明書認証 |
| API認証 | P0 | Service-to-Service M2Mトークン (Client Credentials) |
| 生体認証 | P2 | モバイル端末の指紋/FaceID |

### 2.2 認可方式
| 機能 | 優先度 | 説明 |
|---|---|---|
| RBAC | P0 | ロールベースアクセス制御（現場作業員→所長→経営層） |
| ABAC | P1 | 属性ベース制御（プロジェクト・現場・期間） |
| ゼロトラスト | P1 | 常時検証、最小権限、マイクロセグメンテーション |
| API認可 | P0 | OAuth 2.0 Scopeベース |
| データレベル認可 | P2 | 行レベルセキュリティ（プロジェクト単位の参照制限） |

### 2.3 ユーザー管理
| 機能 | 優先度 | 説明 |
|---|---|---|
| 組織管理 | P0 | 会社→事業部→現場の階層構造 |
| ユーザーライフサイクル | P0 | 登録→承認→有効化→一時停止→無効化→削除 |
| 協力会社ポータル | P0 | 外部ユーザー自己登録・管理 |
| 一括インポート | P1 | CSV/HRシステム連携 |

## 3. データモデル

```sql
-- 組織
organizations (
    id UUID PK,
    parent_id UUID FK -> organizations.id,
    name VARCHAR(255) NOT NULL,
    type ENUM('company', 'department', 'site', 'partner'),
    status ENUM('active', 'inactive'),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)

-- ユーザー
users (
    id UUID PK,
    organization_id UUID FK -> organizations.id,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255),
    display_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    locale VARCHAR(10) DEFAULT 'ja',
    status ENUM('pending', 'active', 'suspended', 'deactivated'),
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    last_login_at TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)

-- ロール
roles (
    id UUID PK,
    organization_id UUID FK -> organizations.id,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ
)

-- 権限
permissions (
    id UUID PK,
    resource VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    UNIQUE(resource, action)
)

-- ロール→権限 中間テーブル
role_permissions (
    role_id UUID FK -> roles.id,
    permission_id UUID FK -> permissions.id,
    PRIMARY KEY(role_id, permission_id)
)

-- ユーザー→ロール 中間テーブル
user_roles (
    user_id UUID FK -> users.id,
    role_id UUID FK -> roles.id,
    assigned_at TIMESTAMPTZ,
    assigned_by UUID FK -> users.id,
    expires_at TIMESTAMPTZ,
    PRIMARY KEY(user_id, role_id)
)

-- リフレッシュトークン
refresh_tokens (
    id UUID PK,
    user_id UUID FK -> users.id,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
)

-- APIクライアント (M2M)
api_clients (
    id UUID PK,
    organization_id UUID FK -> organizations.id,
    name VARCHAR(255) NOT NULL,
    client_id VARCHAR(100) UNIQUE NOT NULL,
    client_secret_hash VARCHAR(255) NOT NULL,
    scopes TEXT[] NOT NULL,
    status ENUM('active', 'revoked'),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)

-- 監査ログ
auth_audit_logs (
    id BIGSERIAL PK,
    user_id UUID,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
)
-- パーティション: 月次
```

## 4. API エンドポイント

```
POST   /api/v1/auth/login              # ログイン（JWT発行）
POST   /api/v1/auth/logout             # ログアウト（トークン無効化）
POST   /api/v1/auth/refresh            # トークンリフレッシュ
POST   /api/v1/auth/mfa/setup          # MFA設定開始
POST   /api/v1/auth/mfa/verify         # MFA検証
POST   /api/v1/auth/mfa/disable        # MFA無効化

GET    /api/v1/users                   # ユーザー一覧
POST   /api/v1/users                   # ユーザー作成
GET    /api/v1/users/{id}              # ユーザー詳細
PUT    /api/v1/users/{id}              # ユーザー更新
DELETE /api/v1/users/{id}              # ユーザー削除
POST   /api/v1/users/{id}/roles        # ロール付与

GET    /api/v1/roles                   # ロール一覧
POST   /api/v1/roles                   # ロール作成
GET    /api/v1/roles/{id}              # ロール詳細
PUT    /api/v1/roles/{id}              # ロール更新
DELETE /api/v1/roles/{id}              # ロール削除
POST   /api/v1/roles/{id}/permissions  # 権限付与

GET    /api/v1/permissions             # 権限一覧

POST   /api/v1/api-clients             # APIクライアント登録
GET    /api/v1/api-clients             # APIクライアント一覧
DELETE /api/v1/api-clients/{id}        # APIクライアント削除（失効）

GET    /api/v1/audit-logs              # 監査ログ検索
```

## 5. トークン設計

```
Access Token (JWT):
{
    "sub": "user-uuid",
    "org": "org-uuid",
    "roles": ["site-manager", "inspector"],
    "scopes": ["read:documents", "write:reports"],
    "device_id": "device-uuid",
    "iat": 1716393600,
    "exp": 1716397200,   // 1時間
    "iss": "construction-enterprise-os-auth",
    "jti": "unique-token-id"
}

Refresh Token:
- 暗号化してDB(ハッシュ)保存
- 有効期限: 30日（モバイル）/ 7日（Web）
- ローテーション方式（使用ごとに新しいトークン発行）

M2M Token (Client Credentials):
{
    "sub": "client-uuid",
    "client_name": "iot-gateway",
    "org": "org-uuid",
    "scopes": ["ingest:iot-data", "read:sensors"],
    "iat": ...,
    "exp": ...,   // 24時間
    "iss": "construction-enterprise-os-auth",
    "jti": "..."
}
```

## 6. セキュリティ要件

- パスワード: bcrypt (cost >= 12)
- JWT: RS256 (非対称鍵)
- MFA: TOTP (RFC 6238), バックアップコード(使い切り)
- ロックアウト: 5回連続失敗で15分ロック
- セッション管理: デバイス別セッション一覧、強制ログアウト
- レート制限: /auth/login は IPごとに 10回/分

## 7. サービス構成

```
services/auth/
├── main.py                  # FastAPI アプリケーション
├── config.py                # 設定管理
├── models/                  # SQLAlchemy モデル
├── schemas/                 # Pydantic スキーマ
├── api/                     # ルーター
│   ├── auth.py              # 認証エンドポイント
│   ├── users.py             # ユーザー管理
│   ├── roles.py             # ロール管理
│   ├── permissions.py       # 権限管理
│   └── audit.py             # 監査ログ
├── services/                # ビジネスロジック
│   ├── auth_service.py
│   ├── token_service.py
│   ├── mfa_service.py
│   └── audit_service.py
├── middleware/
│   ├── auth_middleware.py    # JWT検証
│   └── rbac_middleware.py   # ロール検証
├── tests/
├── alembic/                  # マイグレーション
├── Dockerfile
└── requirements.txt
```
