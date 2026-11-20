-- Run only in a fresh disposable database with the workbook SQL draft applied.
-- Current directory must contain kjv-stage.csv and the offline hosted-kjv.csv.
\set ON_ERROR_STOP on
BEGIN;

INSERT INTO bta_scripture.edition
    (edition_code, translation_family, display_name, language_tag, script_code)
VALUES ('KJV', 'KJV', 'King James Version', 'en', 'Latn');

INSERT INTO bta_scripture.import_batch
    (edition_id, source_record_id, source_url, source_revision, source_format,
     source_sha256, file_bytes, acquired_on)
SELECT edition_id, 'KJV-01', :'source_url', :'source_revision', 'OSIS',
       :'source_sha256', :'file_bytes'::bigint, :'acquired_on'::date
FROM bta_scripture.edition WHERE edition_code = 'KJV';

\copy bta_scripture.verse_stage (batch_id,row_number,source_reference,source_book_code,source_chapter_label,source_verse_label,book_code,book_name,book_order,chapter_number,verse_order,verse_label,verse_text) FROM 'kjv-stage.csv' WITH (FORMAT csv, ENCODING 'UTF8')

CREATE TEMP TABLE expected_hosted_kjv (
    book_code text, chapter_number smallint, address_label text, verse_text text,
    PRIMARY KEY (book_code, chapter_number, address_label)
) ON COMMIT DROP;

\copy expected_hosted_kjv FROM 'hosted-kjv.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

CREATE TEMP VIEW fixture_matches AS
SELECT e.book_code, e.chapter_number, e.address_label,
       count(s.row_number) AS address_matches,
       bool_and(
           btrim(regexp_replace(s.verse_text, '[[:space:]]+', ' ', 'g')) =
           btrim(regexp_replace(e.verse_text, '[[:space:]]+', ' ', 'g'))
       ) AS wording_matches
FROM expected_hosted_kjv AS e
LEFT JOIN bta_scripture.verse_stage AS s
    ON (s.book_code, s.chapter_number, s.verse_label) =
       (e.book_code, e.chapter_number, e.address_label)
GROUP BY e.book_code, e.chapter_number, e.address_label;

SELECT count(*) AS verses, count(DISTINCT book_code) AS books,
       count(DISTINCT (book_code, chapter_number)) AS chapters
FROM bta_scripture.verse_stage;

SELECT * FROM fixture_matches ORDER BY book_code, chapter_number, address_label;

DO $$
BEGIN
    IF (SELECT count(*) FROM bta_scripture.verse_stage) <> 31102 OR
       (SELECT count(DISTINCT book_code) FROM bta_scripture.verse_stage) <> 66 OR
       (SELECT count(DISTINCT (book_code, chapter_number)) FROM bta_scripture.verse_stage) <> 1189 OR
       (SELECT count(DISTINCT (book_code, chapter_number, verse_label)) FROM bta_scripture.verse_stage) <> 31102 OR
       (SELECT count(*) FROM fixture_matches WHERE address_matches = 1 AND wording_matches) <> 11 OR
       (SELECT count(*) FROM expected_hosted_kjv) <> 11 OR
       EXISTS (SELECT FROM bta_scripture.snapshot) OR
       EXISTS (SELECT FROM bta_scripture.active_edition)
    THEN
        RAISE EXCEPTION 'Isolated KJV staging validation failed';
    END IF;
END $$;

ROLLBACK;

DO $$
BEGIN
    IF EXISTS (SELECT FROM bta_scripture.edition) OR
       EXISTS (SELECT FROM bta_scripture.import_batch) OR
       EXISTS (SELECT FROM bta_scripture.verse_stage) OR
       EXISTS (SELECT FROM bta_scripture.snapshot) OR
       EXISTS (SELECT FROM bta_scripture.active_edition)
    THEN
        RAISE EXCEPTION 'Isolated transaction left rows behind';
    END IF;
END $$;
