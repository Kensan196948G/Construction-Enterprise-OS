# Construction Enterprise OS (CEO-OS)

建設・土木業向け統合オペレーティングシステム。

## 概要

CEO-OSは建設・土木業における全業務・全データ・全プロセスを統合するデジタル基盤です。
個別バラバラの業務アプリケーション群を「OSレイヤ」によって統合し、単一の真実として機能させます。

### OSレイヤ構造

```
Construction Enterprise OS
├── Layer 0: インフラ基盤 (K8s, PostgreSQL, Redis, MinIO, ES)
├── Layer 1: 共通基盤 (認証, データ, API GW, イベント, 通知, ログ, UI)
├── Layer 2: ドメイン基盤 (AI, IoT, GIS, BIM, 文書, ワークフロー)
├── Layer 3: 業務アプリケーション (ERP, 現場DX, 協力会社連携 他)
└── Layer 4: セキュリティ・統制 (SOC, SIEM, ゼロトラスト)
```

## 技術スタック

| レイヤ | 技術 |
|---|---|
| フロントエンド | React 18 + Next.js 14 |
| バックエンド | Python 3.12 + FastAPI |
| データベース | PostgreSQL 16 + PostGIS + TimescaleDB |
| キャッシュ | Redis 7 |
| メッセージ | RabbitMQ / Kafka |
| 検索 | Elasticsearch 8 |
| オブジェクトストレージ | MinIO (S3互換) |
| AI/ML | PyTorch + LangChain + LlamaIndex |
| コンテナ | Docker + Kubernetes |
| CI/CD | GitHub Actions |
| モノレポ | pnpm workspaces + Turborepo |

## 開発環境セットアップ

### 必要条件

- Node.js >= 20
- pnpm >= 9
- Python >= 3.12
- Docker & Docker Compose

### 起動

```bash
# リポジトリクローン
git clone <repository-url>
cd ceo-os

# 依存パッケージインストール
pnpm install

# インフラ起動 (PostgreSQL, Redis, Kafka 他)
pnpm docker:up

# 開発サーバー起動
pnpm dev
```

## プロジェクト構造

```
ceo-os/
├── apps/              # フロントエンドアプリケーション
├── services/          # バックエンド マイクロサービス
├── packages/          # 共有パッケージ (UI, core, db, etc.)
├── infra/             # IaC (Terraform, K8s)
├── docs/              # 設計ドキュメント
│   └── architecture/  # アーキテクチャ設計書
├── scripts/           # 開発用スクリプト
├── docker-compose.yml # 開発環境
└── turbo.json         # Turborepo設定
```

## フェーズ計画

| フェーズ | 期間 | 内容 |
|---|---|---|
| Phase 0 | M1-2 | 基盤構築・認証基盤MVP |
| Phase 1 | M3-5 | OSカーネル完成 (API GW, イベント, ログ, 通知, UI) |
| Phase 2 | M6-9 | ドメイン基盤 (文書, WF, GIS, AI, IoT) |
| Phase 3 | M10-14 | 業務アプリケーション |
| Phase 4 | M12-16 | セキュリティ・統制 |
| Phase 5 | M15-18 | 安定化・リリース |

## ドキュメント

- [全体アーキテクチャ設計](docs/architecture/00-overview.md)
- [統合認証基盤 詳細設計](docs/architecture/01-auth-platform.md)
- [統合データ基盤 詳細設計](docs/architecture/02-data-platform.md)
- [API Gateway & イベント基盤](docs/architecture/03-api-gateway.md)
- [共通UI・通知・ログ基盤](docs/architecture/04-common-platforms.md)

## ライセンス

Proprietary - All Rights Reserved

---

**最終更新**: 2026-05-24
