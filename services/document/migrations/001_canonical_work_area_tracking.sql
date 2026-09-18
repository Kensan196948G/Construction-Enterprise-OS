-- Adds tracking columns for internal canonical/work-area storage requests
-- triggered by the workflow service. Additive only; no data is modified.
ALTER TABLE document.documents ADD COLUMN IF NOT EXISTS canonical_stored_at timestamptz NULL;
ALTER TABLE document.documents ADD COLUMN IF NOT EXISTS work_area_receipt_no varchar(30) NULL;
ALTER TABLE document.documents ADD COLUMN IF NOT EXISTS work_area_stored_at timestamptz NULL;
