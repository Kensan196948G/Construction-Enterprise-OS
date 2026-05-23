# CEO-OS 開発用 Makefile

.PHONY: help dev up down build test lint clean

help: ## ヘルプ表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# Docker 開発環境
# ============================================
up: ## 開発インフラ起動 (PostgreSQL, Redis, Kafka 他)
	docker compose up -d

down: ## 開発インフラ停止
	docker compose down

logs: ## コンテナログ表示
	docker compose logs -f

reset: ## 開発データ完全リセット
	docker compose down -v
	docker compose up -d

# ============================================
# バックエンド (Python/FastAPI)
# ============================================
auth-dev: ## Auth Service開発サーバー起動
	cd services/auth && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

auth-test: ## Auth Serviceテスト実行
	cd services/auth && python -m pytest tests/ -v -p no:flask

auth-lint: ## Auth Service lint実行
	cd services/auth && ruff check src/

auth-typecheck: ## Auth Service型チェック
	cd services/auth && mypy src/

# ============================================
# フロントエンド (Next.js)
# ============================================
web-dev: ## Webアプリ開発サーバー起動
	cd apps/web && pnpm dev

# ============================================
# データベース
# ============================================
db-migrate: ## マイグレーション実行
	cd services/auth && alembic upgrade head

db-rollback: ## マイグレーションを1つ戻す
	cd services/auth && alembic downgrade -1

db-seed: ## シードデータ投入
	@echo "シードデータは Docker起動時に自動投入されます"

# ============================================
# コード品質
# ============================================
test: auth-test ## 全テスト実行

lint: auth-lint ## 全lint実行

format: ## コードフォーマット
	cd services/auth && ruff format src/
	prettier --write "**/*.{ts,tsx,json,md,yaml,yml}"

# ============================================
# Git
# ============================================
git-status: ## Git状態確認
	git status

git-log: ## Gitログ表示
	git log --oneline -20
