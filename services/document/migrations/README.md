# Document schema migrations

Document has no runtime `create_all`; apply these SQL files with the
database schema owner before deploying the corresponding service code.
All files are idempotent and additive, and may be re-applied safely.

```sh
for f in services/document/migrations/0*.sql; do
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done
```

Apply in filename order:

| File | Purpose |
|---|---|
| `000_base_schema.sql` | Creates `document` schema, the `document_type` / `document_status` ENUMs, `documents`, `document_versions` and their indexes. Matches `services/document/src/models/__init__.py` exactly. |
| `001_canonical_work_area_tracking.sql` | Adds nullable `canonical_stored_at` / `work_area_receipt_no` / `work_area_stored_at`. No-op on a database created by `000`. |
| `002_storage_transfer_result.sql` | Adds nullable `canonical_path` / `work_area_path` / `storage_backend` / `storage_error` used to record the result of the physical file transfer. |

## 正本・作業領域の保存先設定

`POST /api/v1/documents/internal/{id}/store-canonical` and
`.../store-work-area` copy the object stored in MinIO to the canonical
storage. The destination is selected from configuration:

* `ONEDRIVE_ENABLED=true` with `ONEDRIVE_TENANT_ID`, `ONEDRIVE_CLIENT_ID`,
  `ONEDRIVE_CLIENT_SECRET`, `ONEDRIVE_DRIVE_ID` → uploaded to OneDrive
  (Microsoft Graph).
* otherwise `CANONICAL_STORAGE_ROOT` (mounted as the `document-canonical`
  volume in `docker-compose.yml`) → written to the local filesystem.

If neither is configured the endpoints **fail closed** with
`503 STORAGE_NOT_CONFIGURED` and record the failure in
`documents.storage_error`. They never report success without having stored
the file, so the workflow service surfaces
「正本保存に失敗しました」instead of silently succeeding.

## `INTERNAL_API_KEY` の扱い

`INTERNAL_API_KEY` is fail-closed: while it is empty, every internal
endpoint returns `403 INTERNAL_AUTH_REQUIRED`. Set it (the compose
variable is `DOCUMENT_INTERNAL_API_KEY`) **after** these migrations have
been applied — that is what the earlier note meant; an empty key disables
the integration rather than leaving it open.
