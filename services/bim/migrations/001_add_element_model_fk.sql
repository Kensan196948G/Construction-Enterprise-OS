-- 既存データベース向け: bim.bim_elements.model_id に外部キー制約を追加する。
--
-- 000_base_schema.sql は CREATE TABLE IF NOT EXISTS で作るため、すでに
-- bim_elements が存在するデータベースには制約が追加されない。ORM 側で
-- relationship を解決するには制約が必要 (無いと mapper 構成が
-- NoForeignKeysError で失敗し、BIM サービスの DB アクセスが全滅する)。
--
-- 孤立行があると制約追加が失敗するため、先に検査して明示的に中止する。
-- 冪等: 制約が既にあれば何もしない。データは変更しない。

DO $$
DECLARE
    orphan_count bigint;
BEGIN
    IF to_regclass('bim.bim_elements') IS NULL THEN
        RAISE NOTICE 'bim.bim_elements が存在しないためスキップします';
        RETURN;
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint c
        WHERE c.conname = 'bim_elements_model_id_fkey'
          AND c.conrelid = 'bim.bim_elements'::regclass
    ) THEN
        RAISE NOTICE 'bim_elements_model_id_fkey は既に存在します';
        RETURN;
    END IF;

    SELECT count(*) INTO orphan_count
    FROM bim.bim_elements e
    LEFT JOIN bim.bim_models m ON m.id = e.model_id
    WHERE m.id IS NULL;

    IF orphan_count > 0 THEN
        RAISE EXCEPTION
            '孤立した bim_elements.model_id が % 件あります。先に解消してください。',
            orphan_count;
    END IF;

    ALTER TABLE bim.bim_elements
        ADD CONSTRAINT bim_elements_model_id_fkey
        FOREIGN KEY (model_id) REFERENCES bim.bim_models (id) ON DELETE CASCADE;
END
$$;
