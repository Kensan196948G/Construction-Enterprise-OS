-- Records the result of the physical canonical / work-area file transfer.
-- Additive only; existing rows are left untouched (all columns nullable).
-- 正本保存と作業領域保存で結果を共有すると、後の成功が前の失敗を上書きして
-- しまうため、操作ごとに分離している。
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS canonical_storage_backend varchar(20) NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS canonical_storage_error text NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS work_area_storage_backend varchar(20) NULL;
ALTER TABLE document.documents
    ADD COLUMN IF NOT EXISTS work_area_storage_error text NULL;
