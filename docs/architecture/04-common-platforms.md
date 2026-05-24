# 共通UIコンポーネント & 通知・ログ基盤 詳細設計

## 1. 共通UIコンポーネントライブラリ (Design System)

### 1.1 責務
Construction-Enterprise-OS全画面の統一されたUI/UXを提供する「OSのGUI層」。
全サービスが同じコンポーネントを使用し、見た目・操作性・アクセシビリティを統一する。

### 1.2 技術選定

| 項目 | 選択 |
|---|---|
| フレームワーク | Next.js 14 (App Router) |
| UIライブラリ | shadcn/ui + Radix UI (ヘッドレスコンポーネント) |
| スタイリング | Tailwind CSS |
| アイコン | Lucide Icons |
| フォーム | React Hook Form + Zod バリデーション |
| テーブル | TanStack Table (React Table v8) |
| グラフ | Recharts / Nivo |
| 地図 | MapLibre GL JS / CesiumJS |
| PDFビューア | react-pdf |
| 状態管理 | Zustand (軽量) |
| テスト | Vitest + Testing Library |

### 1.3 コンポーネント体系

```text
packages/ui/src/
├── primitives/           # 基本UI要素
│   ├── Button/
│   ├── Input/
│   ├── Select/
│   ├── Checkbox/
│   ├── Radio/
│   ├── Switch/
│   ├── Textarea/
│   ├── Badge/
│   ├── Tooltip/
│   ├── Dialog/
│   ├── Sheet/            # スライドパネル
│   ├── DropdownMenu/
│   └── Skeleton/         # ローディングプレースホルダ
│
├── layout/               # レイアウトコンポーネント
│   ├── AppShell/         # 全体レイアウト（サイドナビ + ヘッダー + コンテンツ）
│   ├── Header/
│   ├── Sidebar/
│   ├── Footer/
│   ├── Breadcrumb/
│   └── PageContainer/
│
├── data-display/         # データ表示
│   ├── DataTable/        # サーバーサイドページネーション対応テーブル
│   ├── DataCard/         # カード形式表示
│   ├── StatCard/         # 統計数値カード
│   ├── Timeline/         # タイムライン表示
│   ├── TreeView/         # 組織・フォルダツリー
│   └── Map/              # 地図表示ラッパー
│
├── forms/                # フォーム系
│   ├── FormField/        # ラベル + エラー表示付き
│   ├── DatePicker/
│   ├── FileUpload/       # ドラッグ&ドロップアップロード
│   ├── RichTextEditor/   # TipTapベース
│   ├── SignaturePad/     # 電子署名
│   └── QRCodeScanner/    # 現場用QR読取
│
├── feedback/             # フィードバック
│   ├── Toast/
│   ├── Alert/
│   ├── ConfirmDialog/
│   └── ProgressBar/
│
├── auth/                 # 認証関連
│   ├── LoginForm/
│   ├── MFAVerification/
│   ├── PasswordChange/
│   └── SessionManager/
│
├── workflow/             # ワークフロー
│   ├── ApprovalCard/
│   ├── ApprovalHistory/
│   └── WorkflowDesigner/ # ワークフロー設計画面
│
├── document/             # 文書管理
│   ├── PDFViewer/
│   ├── ImageViewer/
│   ├── DocumentCard/
│   └── VersionHistory/
│
└── mobile/               # モバイル特化
    ├── BottomSheet/
    ├── PullToRefresh/
    ├── OfflineIndicator/
    ├── CameraCapture/
    └── GPSLocationPicker/
```

### 1.4 デザイントークン

```css
/* 建設業向けカラーパレット */
:root {
  --color-primary: #1a56db;        /* 信頼の青 */
  --color-safety-orange: #f97316;  /* 安全第一 */
  --color-site-yellow: #eab308;    /* 注意喚起 */
  --color-danger-red: #dc2626;     /* 危険・停止 */
  --color-approve-green: #16a34a;  /* 承認・安全 */
  --color-concrete-gray: #9ca3af;  /* コンクリート */
  --color-soil-brown: #92400e;     /* 土系 */

  /* 建設業フォント */
  --font-sans: 'Noto Sans JP', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

## 2. 統合通知基盤

### 2.1 責務
全サービスから発行される通知を集約し、適切なチャネルで配信する「OSの通知センター」。

### 2.2 配信チャネル

| チャネル | 用途 | 優先度 |
|---|---|---|
| アプリ内通知 | リアルタイム通知（WebSocket）| P0 |
| Email | 重要通知・レポート | P0 |
| SMS | 緊急通知（災害・事故）| P1 |
| LINE / Teams | チャット連携 | P1 |
| プッシュ通知 | モバイル端末向け | P1 |
| Webhook | 外部システム通知 | P2 |

### 2.3 通知テンプレート

```python
# 通知テンプレート
notification_templates (
    id UUID PK,
    code VARCHAR(100) UNIQUE NOT NULL,   # "workflow.approval_requested"
    name VARCHAR(255) NOT NULL,
    channels TEXT[] NOT NULL,            # ["in_app", "email"]
    title_template TEXT,                 # "【要承認】{document_name}"
    body_template TEXT,                  # "承認依頼があります。期限: {deadline}"
    priority ENUM('low', 'normal', 'high', 'urgent'),
    category ENUM('workflow', 'safety', 'system', 'iot', 'document'),
    created_at TIMESTAMPTZ
)

# 通知
notifications (
    id BIGSERIAL PK,
    template_id UUID FK,
    recipient_id UUID FK,          # users.id
    title VARCHAR(500) NOT NULL,
    body TEXT,
    metadata JSONB,                # 関連リソースURL等
    channels TEXT[] NOT NULL,      # 実際の配信チャネル
    status ENUM('pending', 'sent', 'read', 'failed'),
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);
```

## 3. 統合ログ基盤 (ELK Stack)

### 3.1 責務
全サービス・全インフラのログを集約・検索・可視化する「OSの診断システム」。

### 3.2 ログレベルとカテゴリ

```python
# 共通ログフォーマット
{
    "timestamp": "2026-05-24T12:00:00.000Z",
    "level": "INFO",              # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "service": "auth-service",
    "trace_id": "abc123",         # 分散トレーシングID
    "span_id": "def456",
    "user_id": "uuid",
    "organization_id": "uuid",
    "action": "user.login",
    "resource": "/api/v1/auth/login",
    "method": "POST",
    "status_code": 200,
    "duration_ms": 45,
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "message": "User login successful",
    "extra": {}
}
```

### 3.3 収集対象

| ログ種別 | 収集方法 | 保存期間 |
|---|---|---|
| アプリケーションログ | Filebeat → Logstash → ES | 90日 |
| APIアクセスログ | API Gateway → Kafka → Logstash | 1年 |
| 監査ログ | サービス → Kafka → PostgreSQL + ES | 10年 |
| システムログ | Metricbeat | 90日 |
| IoTデバイスログ | MQTT → Kafka → ES | 30日 |
| セキュリティログ | Wazuh → ES | 1年 |

### 3.4 Pythonロギング共通設定

```python
# packages/logging/src/construction-os_logger.py
import logging
import structlog
from opentelemetry import trace

def setup_logging(service_name: str):
    """全サービス共通のロギング設定"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            # OpenTelemetry トレースID注入
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    return structlog.get_logger(service_name=service_name)

# 使用例
logger = setup_logging("auth-service")
logger.info("user.login", user_id="xxx", ip="192.168.1.1")
logger.error("db.connection_failed", error=str(e), db_host="pg-master")
```

## 4. 統合検索基盤

### 4.1 責務
Construction-Enterprise-OS内の全コンテンツに対する統合検索を提供する。

### 4.2 アーキテクチャ

```
┌────────────────────────────────────────┐
│           Unified Search API           │
│         /api/v1/search?q=...          │
└────────────────┬───────────────────────┘
                 │
    ┌────────────┼────────────┬──────────┐
    ▼            ▼            ▼          ▼
┌───────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│文書   │ │図面/CAD  │ │BIM    │ │GIS/地図  │
│全文検索│ │メタデータ│ │モデル │ │空間検索  │
└───┬───┘ └────┬─────┘ └───┬────┘ └────┬─────┘
    ▼          ▼           ▼          ▼
┌──────────────────────────────────────────┐
│          Elasticsearch 8                 │
│  ┌────────────────────────────────────┐  │
│  │ 統合インデックス                    │  │
│  │ - documents (PDF, 図面, 写真)      │  │
│  │ - bim_components                   │  │
│  │ - geo_locations (GeoJSON)          │  │
│  │ - knowledge_articles               │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

これらの基盤の上に、各ドメイン基盤（AI, IoT, GIS, BIM, 文書管理, ワークフロー）および業務アプリケーション（ERP, 現場DX, 協力会社連携等）が構築される。
