# Construction Enterprise OS (CEO-OS) 全体アーキテクチャ設計書

## 1. プロジェクト定義

### 1.1 名称
**Construction Enterprise OS（CEO-OS）** — 建設・土木業向け統合オペレーティングシステム

### 1.2 目的
建設・土木業における全業務・全データ・全プロセスを統合するデジタル基盤を提供する。
個別バラバラの業務アプリケーション群を「OSレイヤ」によって統合し、単一の真実として機能させる。

### 1.3 対象ユーザー
- 建設・土木事業者（ゼネコン、サブコン、専門工事会社）
- 協力会社・下請け事業者
- 発注者・監理者（官公庁含む）
- 現場作業員・現場監督
- 経営層・管理部門

### 1.4 技術スタック
| レイヤ | 技術 |
|---|---|
| フロントエンド | React 18 + Next.js 14 (App Router) |
| バックエンド | Python 3.12 + FastAPI |
| データベース | PostgreSQL 16 + PostGIS + TimescaleDB |
| キャッシュ | Redis |
| メッセージキュー | RabbitMQ / Apache Kafka |
| オブジェクトストレージ | MinIO (S3互換) |
| 検索エンジン | Elasticsearch |
| AI/ML | PyTorch + LangChain + LlamaIndex |
| コンテナ | Docker + Kubernetes |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| モノレポ管理 | pnpm workspaces + Turborepo |

---

## 2. OSレイヤ アーキテクチャ

### 2.1 レイヤ構造

```text
Construction Enterprise OS
│
├── Layer 0: インフラストラクチャ基盤
│   ├── Container Orchestration (K8s)
│   ├── Service Mesh (Istio)
│   ├── Storage (PostgreSQL, Redis, MinIO, Elasticsearch)
│   └── Network & Security
│
├── Layer 1: 共通基盤（OSカーネル相当）
│   ├── 統合認証基盤 (AuthN/AuthZ)
│   ├── 統合データ基盤 (Data Lake & Federation)
│   ├── API Gateway (Kong / Traefik)
│   ├── イベントバス (Kafka / RabbitMQ)
│   ├── 統合ログ基盤 (ELK Stack)
│   ├── 統合通知基盤 (Push / Email / SMS / Webhook)
│   └── 共通UIコンポーネントライブラリ (Design System)
│
├── Layer 2: ドメイン基盤
│   ├── AI統合基盤 (LLM / RAG / Vector DB / Agent)
│   ├── IoT統合基盤 (MQTT / Sensor / Edge / Alert)
│   ├── GIS・地図統合基盤 (PostGIS / MapLibre / Cesium)
│   ├── BIM/CIM統合基盤 (IFC / 3D / Point Cloud / Digital Twin)
│   ├── 文書・図面統合基盤 (PDF / CAD / OCR / Versioning)
│   └── ワークフロー基盤 (BPMN / Camunda / 電子決裁)
│
├── Layer 3: 業務アプリケーション
│   ├── ERP・経営管理 (原価 / 工事台帳 / 予算 / 会計)
│   ├── 現場DX (施工管理 / 出来形 / 品質 / 安全)
│   ├── 協力会社連携 (ポータル / 契約 / 評価)
│   ├── モバイル・オフライン (PWA / 同期 / キャッシュ)
│   ├── 監査・コンプライアンス (証跡 / 監査ログ / 報告)
│   ├── ナレッジマネジメント (Wiki / 教訓DB / 技術継承)
│   └── 分析基盤 (BI / ダッシュボード / 予測)
│
└── Layer 4: セキュリティ・統制
    ├── SOC / SIEM (監視 / 脅威検知 / インシデント対応)
    ├── ゼロトラスト (ZTNA / Micro-segmentation)
    ├── EDR (Endpoint Detection & Response)
    └── コンプライアンス監査
```

### 2.2 レイヤ間通信原則

```
Layer 4 (Security) ──→ All Layers (監視・統制)
Layer 3 (Apps) ──────→ Layer 1 (Gateway経由), Layer 2 (Domain基盤利用)
Layer 2 (Domain) ────→ Layer 1 (Common基盤を利用)
Layer 1 (Common) ────→ Layer 0 (Infra上で稼働)
Layer 0 (Infra) ──────→ (物理/仮想インフラ)
```

### 2.3 データフロー原則

1. **全リクエストはAPI Gatewayを経由**（認証・認可・レート制限・監査ログ）
2. **非同期連携はイベントバス経由**（サービス間疎結合）
3. **全サービスログは統合ログ基盤に集約**（ELK Stack）
4. **マスターデータは統合データ基盤で一元管理**
5. **トランザクションデータは各マイクロサービスが所有**

---

## 3. ディレクトリ構造（モノレポ）

```text
ceo-os/
├── apps/                          # デプロイ可能なアプリケーション
│   ├── web/                       # Next.js フロントエンド（BFF含む）
│   ├── admin/                     # 管理画面
│   └── mobile/                    # PWA / モバイル
│
├── services/                      # バックエンド マイクロサービス
│   ├── auth/                      # 認証基盤サービス
│   ├── gateway/                   # API Gateway設定
│   ├── workflow/                  # ワークフローエンジン
│   ├── document/                  # 文書管理サービス
│   ├── gis/                       # GISサービス
│   ├── iot/                       # IoTサービス
│   ├── ai/                        # AIサービス
│   ├── erp/                       # ERPサービス
│   ├── notification/              # 通知サービス
│   └── search/                    # 検索サービス
│
├── packages/                      # 共有パッケージ (ライブラリ)
│   ├── ui/                        # 共通UIコンポーネント (Design System)
│   ├── core/                      # 共通型定義・定数
│   ├── db/                        # Prisma/DB 共通設定・マイグレーション
│   ├── auth-core/                 # 認証共通ロジック
│   ├── event-core/                # イベントバス共通定義
│   ├── api-client/                # APIクライアント生成
│   └── logging/                   # 統合ログ共通ライブラリ
│
├── infra/                         # Infrastructure as Code
│   ├── terraform/                 # Terraform定義
│   ├── kubernetes/                # K8sマニフェスト
│   └── docker/                    # Docker関連
│
├── docs/                          # ドキュメント
│   ├── architecture/              # アーキテクチャ設計書
│   ├── api/                       # API仕様書
│   ├── guides/                    # 開発ガイド
│   └── decisions/                 # ADR (Architecture Decision Records)
│
├── scripts/                       # 開発用スクリプト
├── .github/                       # GitHub Actions CI/CD
├── package.json                   # Root workspace
├── pnpm-workspace.yaml
├── turbo.json
├── docker-compose.yml             # 開発環境
└── README.md
```

---

## 4. 開発フェーズ計画（1年半）

### Phase 0: 基盤構築 (Month 1-2)
- [ ] モノレポ初期化（pnpm workspaces + Turborepo）
- [ ] 開発環境整備（Docker Compose: PostgreSQL, Redis, RabbitMQ, MinIO, ES）
- [ ] CI/CD パイプライン（GitHub Actions: lint, test, build）
- [ ] 統合認証基盤 MVP（AuthN + RBAC + JWT）
- [ ] 統合データ基盤 スキーマ設計

### Phase 1: OSカーネル完成 (Month 3-5)
- [ ] API Gateway 構築
- [ ] イベントバス基盤
- [ ] 統合ログ・監視基盤（ELK）
- [ ] 統合通知基盤
- [ ] 共通UIコンポーネントライブラリ（Design System v1）

### Phase 2: ドメイン基盤 (Month 6-9)
- [ ] 文書・図面統合基盤
- [ ] ワークフロー基盤（BPMN）
- [ ] GIS・地図統合基盤
- [ ] AI統合基盤（LLM + RAG + Vector DB）
- [ ] IoT統合基盤

### Phase 3: 業務アプリケーション (Month 10-14)
- [ ] ERP・経営管理
- [ ] 現場DX
- [ ] BIM/CIM統合基盤
- [ ] モバイル・オフライン基盤
- [ ] 協力会社連携
- [ ] ナレッジマネジメント
- [ ] 分析基盤

### Phase 4: セキュリティ・統制 (Month 12-16)
- [ ] SOC/SIEM
- [ ] ゼロトラスト実装
- [ ] 監査コンプライアンス
- [ ] ペネトレーションテスト

### Phase 5: 安定化・リリース (Month 15-18)
- [ ] 統合テスト・性能テスト
- [ ] ドキュメント整備
- [ ] 本番リリース準備
- [ ] v1.0 リリース

---

## 5. ADR (Architecture Decision Records)

### ADR-001: モノレポ採用
- **決定**: pnpm workspaces + Turborepoによるモノレポ構成
- **理由**: 複数パッケージの一貫性維持、共有コードの再利用、CI/CD一元管理
- **日付**: 2026-05-24

### ADR-002: FastAPI採用
- **決定**: PythonバックエンドにFastAPIを採用
- **理由**: 非同期ネイティブ、型ヒント、自動OpenAPI生成、高速
- **日付**: 2026-05-24

### ADR-003: PostgreSQL + PostGIS + TimescaleDB
- **決定**: 統合データベースにPostgreSQLを採用し、GIS用にPostGIS、時系列用にTimescaleDBを追加
- **理由**: エコシステムの成熟度、拡張性、OSS
- **日付**: 2026-05-24

### ADR-004: 認証基盤にKeycloakではなく自前実装
- **決定**: 初期MVPは自前JWT認証、成熟後にKeycloak移行を検討
- **理由**: 建設業特化のカスタム要件（協力会社ID、デバイス認証等）の柔軟な実装のため
- **日付**: 2026-05-24

### ADR-005: イベントバスにKafka
- **決定**: 非同期イベント基盤にApache Kafkaを採用
- **理由**: 高スループット、永続性、リプレイ機能。IoTデータストリームにも適合
- **日付**: 2026-05-24
