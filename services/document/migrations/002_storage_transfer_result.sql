-- Records the result of the physical canonical / work-area file transfer.
-- Additive only; existing rows are left untouched (all columns nullable).
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS canonical_path varchar(1000) NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS work_area_path varchar(1000) NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS storage_backend varchar(20) NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS storage_error text NULL;
