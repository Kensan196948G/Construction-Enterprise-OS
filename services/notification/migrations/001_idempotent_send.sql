-- Notification service schema migration.
-- Apply with the notification schema owner before enabling INTERNAL_API_KEY.
ALTER TABLE notification.notifications
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(128);

CREATE UNIQUE INDEX IF NOT EXISTS ix_notifications_idempotency_key
    ON notification.notifications (idempotency_key)
    WHERE idempotency_key IS NOT NULL;
