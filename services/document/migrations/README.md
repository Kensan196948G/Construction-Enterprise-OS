# Document schema migrations

Document has no runtime `create_all`; apply these SQL files with the
database schema owner before deploying the corresponding service code.

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f services/document/migrations/001_canonical_work_area_tracking.sql
```

`001_canonical_work_area_tracking.sql` is additive and adds nullable
tracking columns for the internal canonical/work-area storage endpoints
called by the workflow service. Keep `INTERNAL_API_KEY` empty until this
migration has been applied in the target database.
