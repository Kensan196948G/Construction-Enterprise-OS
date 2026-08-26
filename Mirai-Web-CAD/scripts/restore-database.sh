#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${RESTORE_DATABASE_URL:-}" || -z "${BACKUP_FILE:-}" ]]; then
  echo "RESTORE_DATABASE_URL and BACKUP_FILE are required" >&2
  exit 2
fi

if [[ "${ALLOW_DATABASE_RESTORE:-}" != "yes" ]]; then
  echo "Set ALLOW_DATABASE_RESTORE=yes only for an empty recovery database" >&2
  exit 3
fi

pg_bin="${PG_BIN:-$(pg_config --bindir)}"

"$pg_bin/pg_restore" --dbname="$RESTORE_DATABASE_URL" \
  --exit-on-error \
  --no-owner \
  --no-privileges \
  "$BACKUP_FILE"

verification="$("$pg_bin/psql" "$RESTORE_DATABASE_URL" -v ON_ERROR_STOP=1 -Atc "
  select concat_ws(':',
    (select count(*) from projects),
    (select count(*) from drawings),
    (select count(*) from drawing_versions),
    (select count(*) from audit_logs)
  )
")"

IFS=: read -r projects drawings versions audits <<<"$verification"
if [[ "$projects" -lt 1 || "$drawings" -lt 1 || "$versions" -lt 1 || "$audits" -lt 1 ]]; then
  echo "recovery verification failed: $verification" >&2
  exit 1
fi

echo "database recovery verified: projects=$projects drawings=$drawings versions=$versions audits=$audits"
