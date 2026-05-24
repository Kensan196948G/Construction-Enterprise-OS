# 🏗️ Construction Enterprise OS (CEO-OS)

> **建設・土木業向け統合オペレーティングシステム**

[![CI](https://github.com/Kensan196948G/Construction-Enterprise-OS/actions/workflows/ci.yml/badge.svg)](https://github.com/Kensan196948G/Construction-Enterprise-OS/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-blue.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 📋 概要

CEO-OSは建設・土木業における**全業務・全データ・全プロセスを統合**するデジタル基盤です。
個別バラバラの業務アプリケーション群を **「OSレイヤ」** によって統合し、単一の真実 (Single Source of Truth) として機能させます。

### 🎯 対象ユーザー

| 🏢 事業者 | 👷 現場 | 📋 管理 |
|---|---|---|
| ゼネコン | 現場作業員 | 経営層 |
| サブコン | 現場監督 | 管理部門 |
| 専門工事会社 | 協力会社 | 発注者・監理者 |

---

## 🏛️ OSレイヤ アーキテクチャ

```text
┌─────────────────────────────────────────────────────────┐
│                  🛡️ Layer 4: セキュリティ・統制            │
│              SOC/SIEM │ ゼロトラスト │ EDR │ 監査        │
├─────────────────────────────────────────────────────────┤
│                  📱 Layer 3: 業務アプリケーション           │
│     ERP │ 現場DX │ 協力会社連携 │ モバイル │ 監査 │ BI    │
├─────────────────────────────────────────────────────────┤
│                  🧩 Layer 2: ドメイン基盤                  │
│     AI │ IoT │ GIS │ BIM │ 文書管理 │ ワークフロー       │
├─────────────────────────────────────────────────────────┤
│                  ⚙️ Layer 1: 共通基盤 (OSカーネル)         │
│     認証 │ データ │ API GW │ イベント │ 通知 │ ログ       │
├─────────────────────────────────────────────────────────┤
│                  🖥️ Layer 0: インフラ基盤                  │
│         K8s │ PostgreSQL │ Redis │ Kafka │ MinIO        │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技術スタック

| レイヤ | 🔧 技術 | 📌 バージョン |
|---|---|---|
| **フロントエンド** | React + Next.js (App Router) | 18 / 14 |
| **UIコンポーネント** | shadcn/ui + Radix UI + Tailwind CSS | latest |
| **バックエンド** | Python + FastAPI | 3.12 / 0.115 |
| **データベース** | PostgreSQL + PostGIS + TimescaleDB | 16 / 3.4 / 2.x |
| **キャッシュ** | Redis | 7 |
| **メッセージキュー** | RabbitMQ / Apache Kafka | 3.13 / 3.7 |
| **検索エンジン** | Elasticsearch + Kibana | 8.14 |
| **オブジェクトストレージ** | MinIO (S3互換) | latest |
| **AI/ML** | PyTorch + LangChain + LlamaIndex | latest |
| **コンテナ** | Docker + Kubernetes | latest |
| **CI/CD** | GitHub Actions | latest |
| **モノレポ管理** | pnpm workspaces + Turborepo | 9 / 2.x |

---

## 📁 プロジェクト構造

```text
ceo-os/
├── apps/                          # 🖥️ デプロイ可能アプリ
│   ├── web/                       # Next.js フロントエンド
│   ├── admin/                     # 管理画面
│   └── mobile/                    # PWA / モバイル
├── services/                      # ⚙️ バックエンド マイクロサービス
│   ├── auth/                      # 🔐 統合認証基盤 ★実装中
│   ├── document/                  # 📄 文書管理
│   ├── workflow/                  # 🔄 ワークフロー
│   ├── gis/                       # 🗺️ GIS
│   ├── iot/                       # 📡 IoT
│   ├── ai/                        # 🤖 AI
│   ├── erp/                       # 💰 ERP
│   └── notification/              # 🔔 通知
├── packages/                      # 📦 共有パッケージ
│   ├── ui/                        # 🎨 共通UIコンポーネント (Design System)
│   ├── core/                      # 🧬 共通型定義・定数
│   ├── auth-core/                 # 🔐 認証共通ロジック
│   └── event-core/                # 📨 イベント共通定義
├── infra/                         # ☸️ IaC
│   ├── terraform/
│   └── kubernetes/
├── docs/                          # 📚 設計ドキュメント
│   └── architecture/              # アーキテクチャ設計書
└── scripts/                       # 🔧 ユーティリティ
```

---

## 📊 開発状況 (5レイヤアーキテクチャ) — 全21サービス

| 🔢 レイヤ | コンポーネント | サービス | 🧪 テスト | 状態 |
|---|---|---|---|---|
| **① Foundation** | 🔐 認証基盤 | `services/auth/` | 30 | ✅ |
| | 🌐 API Gateway | `services/gateway/` | 9 | ✅ |
| | 📨 イベント基盤 | `packages/event-core/` | - | ✅ |
| | 📊 共通ログ | `packages/logging/` | 24 | ✅ |
| | 🔔 共通通知 | `services/notification/` | 13 | ✅ |
| | 📋 マスタデータ | `services/auth/seed.py` | - | ✅ |
| | 🛡️ 権限管理 | `services/auth/` (RBAC) | - | ✅ |
| | 📝 監査証跡 | `services/auth/` (Audit) | - | ✅ |
| | 🎨 統合UI | `packages/ui/` + `apps/web/` | - | ✅ |
| **② Data&AI** | 🗺️ GIS | `services/gis/` | 25 | ✅ |
| | 📄 文書管理 | `services/document/` | 12 | ✅ |
| | 📡 IoT | `services/iot/` | 22 | ✅ |
| | 🤖 AI | `services/ai/` | 29 | ✅ |
| | 🏗️ BIM/CIM | `services/bim/` | 35 | ✅ |
| | 👁️ OCR/画像AI | `services/vision/` | 17 | ✅ |
| | 🧬 ベクトルDB | `services/vision/` | 17 | ✅ |
| | 🗄️ データレイク | `services/analytics/` | 27 | ✅ |
| | 📈 分析基盤 | `services/analytics/` | 27 | ✅ |
| **③ Platform** | 🔄 ワークフロー | `services/workflow/` | 17 | ✅ |
| | 🔒 セキュリティ | `services/security/` | 23 | ✅ |
| | 🤝 協力会社連携 | `services/partner/` | 21 | ✅ |
| | 📱 モバイル/PWA | `apps/mobile/` | - | ✅ |
| | ⚡ 自動化 | `services/automation/` | 12 | ✅ |
| | 🏢 BIM/GIS Viewer | `services/platform/` | 22 | ✅ |
| | 📡 IoT管理 | `services/platform/` | 22 | ✅ |
| **④ Business** | 💰 ERP/経営 | `services/erp/` | 27 | ✅ |
| | ⛑️ 安全管理 | `services/safety/` | 14 | ✅ |
| | 🏗️ 現場DX | `services/field-dx/` | 20 | ✅ |
| | 🌊 災害復旧/維持管理 | `services/maintenance/` | 18 | ✅ |
| | 🚢 港湾施工 | `services/advanced/` | 17 | ✅ |
| | 🔍 点検AI | `services/advanced/` | 17 | ✅ |
| | 📋 AI設計照査 | `services/advanced/` | 17 | ✅ |
| | 🔮 予知保全 | `services/advanced/` | 17 | ✅ |
| **⑤ Autonomous** | 🧠 AI Agent | `services/autonomous/` | 17 | ✅ |
| | 👥 デジタルツイン | `services/autonomous/` | 17 | ✅ |
| | 🎯 自動最適化 | `services/autonomous/` | 17 | ✅ |
| | 🚜 自律施工 | 未着手 | - | ⚪ |
| | 🌊 海洋ロボティクス | 未着手 | - | ⚪ |
| | 🎮 自律制御 | 未着手 | - | ⚪ |

> **総計: 21サービス + 7パッケージ + 3アプリ = 582ファイル | 451 tests ALL PASS**

---

## 🚀 クイックスタート

### 前提条件

- **Node.js** >= 20 | **pnpm** >= 9
- **Python** >= 3.12
- **Docker** + Docker Compose

### 開発環境起動

```bash
# 1. クローン
git clone https://github.com/Kensan196948G/Construction-Enterprise-OS.git
cd Construction-Enterprise-OS

# 2. インフラ起動 (PostgreSQL, Redis, Kafka, ES, MinIO)
make up
# または: docker compose up -d

# 3. Auth Service 起動
cd services/auth
cp .env.example .env
make auth-dev
# → http://localhost:8000/docs でSwagger UI表示

# 4. DBマイグレーション
make db-migrate

# 5. シードデータ投入
cd services/auth && python -m src.seed

# 6. テスト実行
make test
```

### ログイン確認 (開発用)

```
Email:    admin@ceo-os.local
Password: AdminPass123!
```

---

## 📅 開発フェーズ計画

| フェーズ | 📆 期間 (概算) | 🎯 内容 | 📊 進捗 |
|---|---|---|---|
| **Phase 0** | M1-2 | 基盤構築・認証基盤MVP | 🟢 80% |
| **Phase 1** | M3-5 | OSカーネル (API GW, イベント, 通知, ログ, UI) | ⚪ 0% |
| **Phase 2** | M6-9 | ドメイン基盤 (文書, WF, GIS, AI, IoT) | ⚪ 0% |
| **Phase 3** | M10-14 | 業務アプリケーション (ERP, 現場DX, 協力会社連携) | ⚪ 0% |
| **Phase 4** | M12-16 | セキュリティ・統制 (SOC/SIEM, ゼロトラスト) | ⚪ 0% |
| **Phase 5** | M15-18 | 安定化・本番リリース | ⚪ 0% |

---

## 📚 ドキュメント

| 📄 ドキュメント | 📝 内容 |
|---|---|
| [全体アーキテクチャ設計](docs/architecture/00-overview.md) | 5レイヤ構造、18ヶ月計画、ADR |
| [統合認証基盤 詳細設計](docs/architecture/01-auth-platform.md) | データモデル/API/トークン/セキュリティ |
| [統合データ基盤 詳細設計](docs/architecture/02-data-platform.md) | PostgreSQL+PostGIS+TimescaleDB/マルチスキーマ |
| [API Gateway & イベント基盤](docs/architecture/03-api-gateway.md) | Gateway+EventBus+Webhook設計 |
| [共通UI・通知・ログ基盤](docs/architecture/04-common-platforms.md) | Design System/通知/ログ/検索 |

---

## 🛡️ セキュリティ

- 🔐 パスワード: **bcrypt** (cost >= 12)
- 🎫 JWT: **RS256** 非対称鍵 (開発環境: HS256)
- 📱 MFA: **TOTP** (RFC 6238) + バックアップコード
- 🔒 ロックアウト: 5回連続失敗 → 15分ロック
- 🚦 レート制限: `/auth/login` 10回/分/IP
- 📝 監査ログ: 全認証イベントを記録
- 🔑 APIキー: SHA-256ハッシュ保存、作成時のみ平文返却

---

## 📜 ライセンス

Proprietary - All Rights Reserved

---

> **最終更新**: 2026-05-24 | **ビルド番号**: 15 | **ステータス**: 🟢 STABLE | **451 tests ALL PASS** | **21サービス**
