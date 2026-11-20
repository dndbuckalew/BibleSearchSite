"""Load two verified Scripture snapshots into the disposable dev PostgreSQL database."""
import argparse
from dataclasses import astuple
import json
from pathlib import Path

from backend.services.scripture_selection import BES, LOCAL
from tools.scripture.import_bes import BES_URL, BES_RIGHTS, load_bes
from tools.scripture.import_kjv import load_pinned_kjv


def postgres_connection():
    import psycopg

    return psycopg.connect(host="127.0.0.1", port=55441, dbname="postgres",
                           user="bta_scripture_test", connect_timeout=3)

def stage_snapshot(cursor, selection, rows, artifact, language, rights, attribution=None):
    edition = selection["edition_id"]
    label = selection["edition_label"]
    cursor.execute(
        """INSERT INTO bta_scripture.edition
           (edition_code, translation_family, display_name, language_tag, script_code)
           VALUES (%s,%s,%s,%s,'Latn') RETURNING edition_id""",
        (edition, edition, label, language),
    )
    edition_id = cursor.fetchone()[0]
    cursor.execute(
        """INSERT INTO bta_scripture.import_batch
           (edition_id, source_record_id, source_url, source_revision, source_format, source_sha256, file_bytes,
            acquired_on, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE,'validated') RETURNING batch_id""",
        (edition_id, artifact["source_record_id"], artifact["source_url"], selection["dataset_revision"],
         artifact["format"], artifact["sha256"], artifact["file_bytes"]),
    )
    batch_id = cursor.fetchone()[0]
    with cursor.copy(
        """COPY bta_scripture.verse_stage
           (batch_id,row_number,source_reference,source_book_code,source_chapter_label,source_verse_label,
            book_code,book_name,book_order,chapter_number,verse_order,verse_label,verse_text) FROM STDIN"""
    ) as copy:
        for number, row in enumerate(rows, 1):
            copy.write_row((batch_id, number, *astuple(row)))
    cursor.execute(
        """INSERT INTO bta_scripture.snapshot
           (edition_id,batch_id,canon_code,versification_code,rights_evidence_ref,attribution_text,
            edition_display_name,scripture_language_tag)
           VALUES (%s,%s,'66-book-dev','source-native-dev',%s,%s,%s,%s) RETURNING snapshot_id""",
        (edition_id, batch_id, rights, attribution, label, language),
    )
    snapshot = cursor.fetchone()[0]
    for table, projection in (
        ("snapshot_book", "DISTINCT %s,book_code,source_book_code,book_name,book_order"),
        ("snapshot_chapter", "DISTINCT %s,book_code,chapter_number"),
        ("verse", "%s,book_code,chapter_number,verse_order,verse_label,source_reference,verse_text"),
        ("verse_address", "%s,book_code,chapter_number,verse_label,verse_order"),
    ):
        cursor.execute(f"INSERT INTO bta_scripture.{table} SELECT {projection} FROM bta_scripture.verse_stage WHERE batch_id=%s",
                       (snapshot, batch_id))
    cursor.execute("INSERT INTO bta_scripture.active_edition VALUES (%s,%s)", (edition_id, snapshot))
    cursor.execute("""SELECT count(DISTINCT book_code),count(DISTINCT (book_code,chapter_number)),count(*)
                      FROM bta_scripture_api.passage_render_v1 WHERE snapshot_id=%s""", (snapshot,))
    counts = cursor.fetchone()
    if counts != (66, 1189, 31102):
        raise ValueError(f"Unexpected database coverage for {edition}: {counts}")
    return {"edition": edition, "snapshot": snapshot, "source_revision": selection["dataset_revision"],
            "counts": dict(zip(("books", "chapters", "verses"), counts, strict=True))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kjv", type=Path)
    parser.add_argument("bes", type=Path)
    args = parser.parse_args()
    manifest, kjv_rows, _ = load_pinned_kjv(args.kjv)
    bes_rows = load_bes(args.bes, kjv_rows)
    with postgres_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM bta_scripture.edition")
        if cursor.fetchone() != (0,):
            raise ValueError("Use a fresh disposable database")
        results = [
            stage_snapshot(cursor, LOCAL, kjv_rows, manifest["artifact"], "en",
                           "KJV scope verified for local dev. Serving rights pending."),
            stage_snapshot(cursor, BES, bes_rows,
                           {"source_record_id": "spabes", "source_url": BES_URL, "format": "USFX",
                            "sha256": BES["dataset_revision"], "file_bytes": args.bes.stat().st_size},
                           "es", BES_RIGHTS, "AudioBiblia.org / Irma Flores · 2026-10-30"),
        ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
