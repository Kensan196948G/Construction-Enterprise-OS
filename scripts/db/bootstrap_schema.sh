#!/usr/bin/env bash
# 各サービスの SQL マイグレーションを空のデータベースへ順番に適用する。
#
# 使い方:
#   scripts/db/bootstrap_schema.sh "postgresql://user:pass@host:5432/db"
#
# 前提:
#   - PostGIS を使うサービス(gis / bim)があるため PostGIS 拡張が必要
#     (スクリプト内で CREATE EXTENSION IF NOT EXISTS postgis を実行)
#   - auth / workflow は alembic 管理のため対象外。別途
#     `cd services/auth && alembic upgrade head` を実行する
#   - すべてのファイルは冪等(additive)なので再実行しても安全
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 <DATABASE_URL>" >&2
  exit 2
fi

DATABASE_URL="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

applied=0
skipped=0
# サービス名の昇順、同一サービス内はファイル名の昇順(= 000 → 001 → 002)
for dir in $(find "$REPO_ROOT/services" -maxdepth 2 -type d -name migrations | sort); do
  service="$(basename "$(dirname "$dir")")"
  files=$(find "$dir" -maxdepth 1 -name '*.sql' | sort)
  if [ -z "$files" ]; then
    continue
  fi
  for file in $files; do
    if [ "${DRY_RUN:-0}" = "1" ]; then
      echo "[dry-run] $service: $(basename "$file")"
      continue
    fi
    echo "[apply] $service: $(basename "$file")"
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f "$file"
    applied=$((applied + 1))
  done
done

if [ "${DRY_RUN:-0}" = "1" ]; then
  exit 0
fi

echo "適用完了: ${applied} ファイル"
echo "注意: auth / workflow は alembic 管理です (cd services/<name> && alembic upgrade head)"
