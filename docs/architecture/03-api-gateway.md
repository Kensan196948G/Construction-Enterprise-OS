# API Gateway & イベント基盤 詳細設計

## 1. API Gateway 設計

### 1.1 責務
全サービス通信の単一入口。認証、認可、ルーティング、レート制限、監査、変換を行う「OSのネットワーク層」。

### 1.2 アーキテクチャ

```
                         Internet / Intranet
                               │
                    ┌──────────▼──────────┐
                    │   WAF / CDN         │
                    └──────────┬──────────┘
                    ┌──────────▼──────────┐
                    │   API Gateway       │
                    │   (Kong / Traefik)  │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │ Auth Plugin    │  │ ← JWT検証, OAuth2
                    │  ├───────────────┤  │
                    │  │ Rate Limit     │  │
                    │  ├───────────────┤  │
                    │  │ Logging        │  │
                    │  ├───────────────┤  │
                    │  │ Transform      │  │
                    │  ├───────────────┤  │
                    │  │ Circuit Break  │  │
                    │  └───────────────┘  │
                    └──┬──┬──┬──┬──┬──┬──┘
                       │  │  │  │  │  │
              ┌────────┘  │  │  │  │  └────────┐
              ▼           ▼  ▼  ▼  ▼           ▼
          auth-svc    workflow document gis   iot-svc
```

### 1.3 ルーティング定義

```yaml
# gateway/routes.yaml
routes:
  - path: /api/v1/auth/*
    service: auth-service
    auth: public  # ログイン・MFAセットアップはpublic
    rate_limit: 100/min
    
  - path: /api/v1/users/*
    service: auth-service
    auth: jwt
    roles: [admin, hr-manager]
    
  - path: /api/v1/documents/*
    service: document-service
    auth: jwt
    
  - path: /api/v1/gis/*
    service: gis-service
    auth: jwt
    
  - path: /api/v1/workflow/*
    service: workflow-service
    auth: jwt
    
  - path: /api/v1/iot/ingest
    service: iot-service
    auth: m2m  # デバイス証明書
    
  - path: /api/v1/ai/*
    service: ai-service
    auth: jwt
    rate_limit: 10/min  # LLM呼び出し制限
```

### 1.4 共通ミドルウェア

```python
# packages/core/src/middleware.py のイメージ

class RequestContext:
    """全サービスで利用するリクエストコンテキスト"""
    request_id: str       # UUID (トレーシング用)
    user_id: str | None
    organization_id: str | None
    roles: list[str]
    scopes: list[str]
    device_id: str | None
    client_ip: str
    user_agent: str
    timestamp: datetime

# 全APIレスポンス共通形式
class APIResponse[T]:
    success: bool
    data: T | None
    error: ErrorDetail | None
    meta: MetaInfo | None  # pagination等
    
class ErrorDetail:
    code: str
    message: str
    details: list[ValidationError] | None
```

## 2. イベント基盤 (Event Bus) 設計

### 2.1 責務
サービス間の非同期・疎結合な連携を実現する「OSのシグナルシステム」。

### 2.2 アーキテクチャ

```
┌──────────────────────────────────────────────────────┐
│                   Event Bus (Kafka)                   │
│                                                      │
│  Producers                    Consumers              │
│  ┌──────────┐              ┌──────────────┐         │
│  │auth-svc  │──┐        ┌─→│notification  │         │
│  │          │  │        │  └──────────────┘         │
│  ├──────────┤  │        │  ┌──────────────┐         │
│  │workflow  │──┤   ┌────┤→│audit-log-svc │         │
│  │          │  │   │    │  └──────────────┘         │
│  ├──────────┤  │   │    │  ┌──────────────┐         │
│  │document  │──┤   │    │→│search-index  │         │
│  │          │  │   │    │  └──────────────┘         │
│  ├──────────┤  │   │    │  ┌──────────────┐         │
│  │iot-svc   │──┤   │    └→│analytics     │         │
│  │          │  │   │       └──────────────┘         │
│  └──────────┘  │   │                                │
│                ▼   ▼                                │
│        ┌──────────────────┐                         │
│        │   Event Topics   │                         │
│        │                  │                         │
│        │ user.created     │                         │
│        │ user.login       │                         │
│        │ doc.uploaded     │                         │
│        │ doc.approved     │                         │
│        │ workflow.started │                         │
│        │ workflow.approved│                         │
│        │ iot.telemetry    │                         │
│        │ iot.alert        │                         │
│        │ project.created  │                         │
│        │ ...              │                         │
│        └──────────────────┘                         │
└──────────────────────────────────────────────────────┘
```

### 2.3 イベント定義

```python
# packages/event-core/src/events.py

from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class CloudEvent:
    """CloudEvents 仕様準拠"""
    specversion: str = "1.0"
    type: str                    # 例: "ceo-os.user.created"
    source: str                  # 例: "/services/auth"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = field(default_factory=datetime.utcnow)
    subject: str | None = None   # 例: user_id
    datacontenttype: str = "application/json"
    data: dict | None = None

# 主要イベントタイプ
class EventTypes:
    # 認証系
    USER_CREATED = "ceo-os.user.created"
    USER_LOGIN = "ceo-os.user.login"
    USER_ROLE_CHANGED = "ceo-os.user.role_changed"
    
    # 文書系
    DOCUMENT_UPLOADED = "ceo-os.document.uploaded"
    DOCUMENT_APPROVED = "ceo-os.document.approved"
    DOCUMENT_VERSIONED = "ceo-os.document.versioned"
    
    # ワークフロー系
    WORKFLOW_STARTED = "ceo-os.workflow.started"
    WORKFLOW_APPROVED = "ceo-os.workflow.approved"
    WORKFLOW_REJECTED = "ceo-os.workflow.rejected"
    
    # IoT系
    IOT_TELEMETRY = "ceo-os.iot.telemetry"
    IOT_ALERT = "ceo-os.iot.alert"
    IOT_DEVICE_ONLINE = "ceo-os.iot.device.online"
    
    # プロジェクト系
    PROJECT_CREATED = "ceo-os.project.created"
    PROJECT_STATUS_CHANGED = "ceo-os.project.status_changed"
```

### 2.4 イベント駆動フロー例: 文書アップロード

```
1. document-svcが doc.uploaded イベントを発行
   ↓
2. search-index-svc が受信 → Elasticsearch にインデックス
3. notification-svc が受信 → 承認者に通知
4. audit-log-svc が受信 → 監査ログ記録
5. workflow-svc が受信 → 自動承認フロー開始（設定による）
```

## 3. 共通APIパターン

### 3.1 REST API 規約

```
# リソース命名: 複数形 kebab-case
GET    /api/v1/construction-sites
POST   /api/v1/construction-sites
GET    /api/v1/construction-sites/{id}
PUT    /api/v1/construction-sites/{id}
DELETE /api/v1/construction-sites/{id}

# ページネーション
GET /api/v1/documents?page=1&per_page=20&sort=created_at&order=desc

# フィルタリング
GET /api/v1/documents?status=approved&project_id=xxx&q=検索キーワード

# バルク操作
POST /api/v1/documents/bulk-archive
{"ids": ["uuid1", "uuid2", "uuid3"]}

# バージョニング: URIパスに v1, v2
# 後方互換性: 非推奨は Deprecation ヘッダ + 6ヶ月猶予
```

### 3.2 API First設計

```
docs/api/
├── openapi/
│   ├── auth.openapi.yaml
│   ├── document.openapi.yaml
│   ├── workflow.openapi.yaml
│   ├── gis.openapi.yaml
│   └── iot.openapi.yaml
└── generated/                # 自動生成
    ├── python-client/
    └── typescript-client/
```

## 4. Webhook基盤

```python
# 外部システム連携用Webhook
webhook_subscriptions (
    id UUID PK,
    organization_id UUID FK,
    url VARCHAR(2048) NOT NULL,     # コールバックURL
    events TEXT[] NOT NULL,          # 購読イベント
    secret VARCHAR(255),             # HMAC署名用シークレット
    headers JSONB,                   # カスタムヘッダー
    status ENUM('active', 'failed', 'disabled'),
    retry_count INT DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ
)
```
