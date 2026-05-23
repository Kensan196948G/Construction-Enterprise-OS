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

## 📊 開発状況

### ✅ 完了済み

| 📦 領域 | 📝 内容 | 🧪 テスト |
|---|---|---|
| 🔐 **認証基盤** | 認証API完全実装 (login/refresh/logout/MFA) | 30/30 PASS |
| 🔐 **ユーザー管理** | ユーザーCRUD + ロール管理 + 権限制御 | ✅ |
| 🔐 **APIクライアント** | M2Mトークン + OAuth2 Client Credentials | ✅ |
| 🎨 **Design System** | 18種 shadcn/ui コンポーネント | - |
| 🏗️ **フロントエンド** | Next.js 14 スケルトン (ランディング/ログイン/ダッシュボード) | - |
| 🗄️ **データベース** | Alembic マイグレーション (10テーブル + 4enum) | ✅ |
| 🗄️ **シードデータ** | 組織・ロール・権限・管理者ユーザー | ✅ |
| 🐳 **Docker環境** | PostgreSQL/Redis/Kafka/ES/MinIO/RabbitMQ | ✅ |
| 🔄 **CI/CD** | GitHub Actions (lint/test/build/security) | ✅ |

### 🚧 実装中 / 次期予定

| 📦 領域 | 📝 予定 | 🎯 優先度 |
|---|---|---|
| 🌐 **API Gateway** | Kong/Traefik 設定 | 🔴 High |
| 📨 **イベント基盤** | Kafka トピック定義 + 発行/購読 | 🔴 High |
| 🔔 **通知基盤** | Email/SMS/Push/InApp | 🟡 Medium |
| 📊 **ログ基盤** | ELK統合 + OpenTelemetry | 🟡 Medium |
| 🗺️ **GIS基盤** | PostGIS API | 🟡 Medium |
| 📄 **文書管理** | MinIO連携 + OCR基盤 | 🟡 Medium |

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

> **最終更新**: 2026-05-24 | **ビルド番号**: 3 | **ステータス**: 🟢 Build Phase
