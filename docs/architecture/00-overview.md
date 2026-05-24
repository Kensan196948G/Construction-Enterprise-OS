# Construction-Enterprise-OS 全体アーキテクチャ設計書

## 1. プロジェクト定義

### 1.1 名称
**Construction-Enterprise-OS** — 建設・土木業向け統合オペレーティングシステム

### 1.2 目的
建設・土木業における全業務・全データ・全プロセスを統合するデジタル基盤を提供する。
個別バラバラの業務アプリケーション群を「OSレイヤ」によって統合し、単一の真実として機能させる。

### 1.3 技術スタック
| レイヤ | 技術 |
|---|---|
| フロントエンド | React 18 + Next.js 14 (App Router) |
| バックエンド | Python 3.12 + FastAPI |
| データベース | PostgreSQL 16 + PostGIS + TimescaleDB |
| キャッシュ | Redis 7 |
| メッセージキュー | Apache Kafka / RabbitMQ |
| オブジェクトストレージ | MinIO (S3互換) |
| 検索エンジン | Elasticsearch 8 |
| AI/ML | LangChain + LlamaIndex + pgvector |
| モノレポ管理 | pnpm workspaces + Turborepo |

---

## 2. OSレイヤ アーキテクチャ

### 2.1 5レイヤ構造

```text
Construction Enterprise OS（建設業統合OS）
│
├── ① Foundation Layer（基礎OS層）
│   ├── 🔐 認証基盤       (Auth Service)
│   ├── 🌐 API Gateway    (Gateway Service)
│   ├── 📨 イベント基盤   (Event Core)
│   ├── 📊 共通ログ       (Logging Package)
│   ├── 🔔 共通通知       (Notification Service)
│   ├── 📋 マスタデータ   (Seed Data / Organizations)
│   ├── 🛡️ 権限管理       (RBAC / Permissions)
│   ├── 📝 監査証跡       (Audit Logs)
│   └── 🎨 統合UI基盤     (Design System / shadcn/ui)
│
├── ② Data & Intelligence Layer（データ・AI層）
│   ├── 🤖 AI基盤         (LLM / RAG / Agent)
│   ├── 🗄️ データレイク   (Data Lake)
│   ├── 🏗️ BIM/CIMデータ  (IFC / 3D Model)
│   ├── 🗺️ GIS            (PostGIS / GeoAlchemy2)
│   ├── 📡 IoTデータ      (Sensor / Telemetry)
│   ├── ⏱️ 時系列DB       (TimescaleDB)
│   ├── 🧬 ベクトルDB     (pgvector)
│   ├── 👁️ OCR/画像AI     (Document AI)
│   └── 📈 分析基盤       (BI / Analytics)
│
├── ③ Platform Layer（共通プラットフォーム層）
│   ├── 📄 文書管理       (Document Service)
│   ├── 🔄 ワークフロー   (Workflow Engine)
│   ├── 📱 モバイル/PWA   (Mobile App)
│   ├── 🤝 協力会社連携   (Partner Portal)
│   ├── 🔒 セキュリティ   (Security Platform)
│   ├── ⚡ 自動化          (RPA / Automation)
│   ├── 🏢 BIM/CIM Viewer (3D Viewer)
│   ├── 🌍 GIS Viewer     (Map Viewer)
│   └── 📡 IoT管理        (Device Management)
│
├── ④ Business Application Layer（業務アプリ層）
│   ├── 🏗️ 現場DX         (Field DX)
│   ├── 🚢 港湾施工管理   (Marine Construction)
│   ├── ⛑️ 安全管理       (Safety Management)
│   ├── 🌊 災害復旧       (Disaster Recovery)
│   ├── 🔧 維持管理       (Maintenance)
│   ├── 🔍 点検AI         (Inspection AI)
│   ├── 💰 ERP/経営       (ERP)
│   ├── 📊 原価管理       (Cost Management)
│   ├── 📐 施工管理       (Construction Mgmt)
│   ├── 📋 AI設計照査     (AI Design Review)
│   └── 🔮 予知保全       (Predictive Maintenance)
│
└── ⑤ Autonomous Layer（自律化層）
    ├── 🧠 AI Agent       (Autonomous Agent)
    ├── 🚜 自律施工       (Autonomous Construction)
    ├── 🎯 自動最適化     (Auto Optimization)
    ├── 👥 デジタルツイン (Digital Twin)
    ├── 🌊 海洋ロボティクス(Marine Robotics)
    └── 🎮 自律制御       (Autonomous Control)
```

### 2.2 レイヤ間責務と依存関係

| レイヤ | 責務 | 依存 |
|---|---|---|
| **① Foundation** | 全サービスの共通インフラ。認証・通信・ログ・通知・UIの統一基盤 | Layer 0 (K8s/DB/Redis/Kafka) |
| **② Data & Intelligence** | データの収集・保存・分析・AI推論。OSの「頭脳」 | ① Foundation (認証/Gateway経由でアクセス) |
| **③ Platform** | 共通業務機能。文書・WF・モバイル・セキュリティ等の水平基盤 | ①② (データ永続化 + 認証) |
| **④ Business Application** | 建設業特化の垂直業務アプリケーション | ①②③ (全下位レイヤを利用) |
| **⑤ Autonomous** | AIによる自律運転・最適化・デジタルツイン連携 | ①②③④ (全レイヤのデータを活用) |

### 2.3 データフロー原則

```
User/Device Request
    │
    ▼
① API Gateway ──→ Auth Service (JWT検証)
    │
    ├──→ ③ Platform Services (文書/WF/通知)
    │        │
    │        └──→ ② Data Services (GIS/IoT/AI)
    │
    ├──→ ④ Business Apps (現場DX/ERP/安全)
    │        │
    │        └──→ ③ Platform + ② Data
    │
    └──→ ⑤ Autonomous (AI Agent/Twin)
             │
             └──→ ② Data Lake + AI + IoT
```

**通信原則**:
1. **同期通信**: REST API (全リクエストはAPI Gateway経由)
2. **非同期通信**: Kafka Event Bus (サービス間連携)
3. **認証**: 全リクエストでJWT検証（① Foundationが保証）
4. **ログ**: 全サービスが共通Logging Packageを使用（②に集約）

---

## 3. 実装状況マッピング

| レイヤ | コンポーネント | サービス/パッケージ | 状態 | テスト |
|---|---|---|---|---|
| **① Foundation** | 認証基盤 | `services/auth/` | ✅ 実装完了 | 30 PASS |
| | API Gateway | `services/gateway/` | ✅ 実装完了 | 9 PASS |
| | イベント基盤 | `packages/event-core/` | ✅ 実装完了 | 検証済 |
| | 共通ログ | `packages/logging/` | ✅ 実装完了 | 24 PASS |
| | 共通通知 | `services/notification/` | ✅ 実装完了 | 13 PASS |
| | マスタデータ | `services/auth/src/seed.py` | ✅ 実装完了 | - |
| | 権限管理 | `services/auth/` (RBAC) | ✅ 実装完了 | 30 PASS |
| | 監査証跡 | `services/auth/` (AuditLog) | ✅ 実装完了 | - |
| | 統合UI基盤 | `packages/ui/` + `apps/web/` | ✅ 実装完了 | - |
| **② Data & Intelligence** | GIS | `services/gis/` | ✅ 実装完了 | 25 PASS |
| | 文書管理 | `services/document/` | ✅ 実装完了 | 12 PASS |
| | AI基盤 | 未着手 | ⚪ | - |
| | データレイク | 未着手 | ⚪ | - |
| | BIM/CIMデータ | 未着手 | ⚪ | - |
| | IoTデータ | 未着手 | ⚪ | - |
| | 時系列DB | Docker設定済 | 🟡 | - |
| | ベクトルDB | 未着手 | ⚪ | - |
| | OCR/画像AI | 未着手 | ⚪ | - |
| | 分析基盤 | 未着手 | ⚪ | - |
| **③ Platform** | ワークフロー | 未着手 | ⚪ | - |
| | モバイル/PWA | 未着手 | ⚪ | - |
| | 協力会社連携 | 未着手 | ⚪ | - |
| | その他 | 未着手 | ⚪ | - |
| **④ Business App** | 全アプリ | 未着手 | ⚪ | - |
| **⑤ Autonomous** | 全機能 | 未着手 | ⚪ | - |

---

## 4. 開発フェーズ計画

| フェーズ | 期間 | 内容 | 対象レイヤ |
|---|---|---|---|
| **Phase 0** | M1-2 | ① Foundation 全基盤実装 | ① |
| **Phase 1** | M3-5 | ② Data & AI基礎 + ③ Platform基盤 | ②③ |
| **Phase 2** | M6-9 | ③ Platform完成 + ④ 業務アプリ着手 | ③④ |
| **Phase 3** | M10-14 | ④ 業務アプリ + ⑤ 自律化層着手 | ④⑤ |
| **Phase 4** | M12-16 | ⑤ 自律化層 + セキュリティ監査 | ⑤ |
| **Phase 5** | M15-18 | 安定化・統合テスト・本番リリース | 全レイヤ |

---

## 5. ADR (Architecture Decision Records)

### ADR-001: 5レイヤアーキテクチャ採用
- **決定**: Foundation → Data&AI → Platform → Business → Autonomous の5層構造
- **理由**: 建設業の特性（現場・データ・自律化）を踏まえた明確な責務分離
- **日付**: 2026-05-24 (改定)

### ADR-002: FastAPI採用
- **決定**: PythonバックエンドにFastAPIを採用
- **理由**: 非同期ネイティブ、型ヒント、自動OpenAPI生成、高速

### ADR-003: PostgreSQL + PostGIS + TimescaleDB
- **決定**: 統合データベースにPostgreSQLを採用
- **理由**: エコシステムの成熟度、拡張性、GIS/時系列対応

### ADR-004: Event Sourcing with Kafka
- **決定**: 非同期イベント基盤にApache Kafkaを採用
- **理由**: 永続性、リプレイ、高スループット。IoTストリームに適合

### ADR-005: Monorepo with pnpm + Turborepo
- **決定**: モノレポ構成で全サービスを単一リポジトリ管理
- **理由**: 一貫性、共有コード再利用、CI/CD一元管理

### ADR-006: GeoAlchemy2 for Spatial Data
- **決定**: GISにGeoAlchemy2 + PostGISを採用
- **理由**: SQLAlchemyとの統合、GeoJSONサポート、空間検索対応
