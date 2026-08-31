# Notification schema migrations

Notification has no runtime `create_all`; apply these SQL files with the
database schema owner before deploying the corresponding service code.

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f services/notification/migrations/001_idempotent_send.sql
```

`001_idempotent_send.sql` is additive and creates a nullable unique key for
internal notification requests. Keep `INTERNAL_API_KEY` empty until this
migration has been applied in the target database.
