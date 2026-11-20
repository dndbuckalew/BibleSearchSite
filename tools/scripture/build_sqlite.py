"""Build a read-only Scripture catalog from the pinned KJV and BES artifacts."""
import argparse
from contextlib import closing
from dataclasses import astuple
from hashlib import file_digest
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from backend.services.scripture_retrieval import normalize
from backend.services.scripture_selection import BES, LOCAL
from tools.scripture.import_bes import BES_RIGHTS, BES_URL, BES_XML_HASH, load_bes
from tools.scripture.import_kjv import load_pinned_kjv

SCHEMA = """
CREATE TABLE snapshot (
    edition TEXT NOT NULL, revision TEXT NOT NULL, language TEXT NOT NULL,
    source_url TEXT NOT NULL, source_sha256 TEXT NOT NULL, rights_notice TEXT NOT NULL,
    PRIMARY KEY (edition, revision)
) WITHOUT ROWID;

CREATE TABLE verse (
    edition TEXT NOT NULL, revision TEXT NOT NULL,
    source_reference TEXT NOT NULL, source_book_code TEXT NOT NULL,
    source_chapter_label TEXT NOT NULL, source_verse_label TEXT NOT NULL,
    book_code TEXT NOT NULL, book_name TEXT NOT NULL, book_order INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL, verse_order INTEGER NOT NULL, verse_label TEXT NOT NULL,
    verse_text TEXT NOT NULL,
    PRIMARY KEY (edition, revision, book_code, chapter_number, verse_order),
    UNIQUE (edition, revision, book_code, chapter_number, verse_label),
    FOREIGN KEY (edition, revision) REFERENCES snapshot
) WITHOUT ROWID;

CREATE TABLE alias (
    alias_key TEXT NOT NULL, book_code TEXT NOT NULL,
    PRIMARY KEY (alias_key, book_code)
) WITHOUT ROWID;
"""


def add_edition(connection, selection, rows, language, source_url, source_hash, rights):
    edition, revision = selection["edition_id"], selection["dataset_revision"]
    connection.execute("INSERT INTO snapshot VALUES (?,?,?,?,?,?)",
                       (edition, revision, language, source_url, source_hash, rights))
    connection.executemany("INSERT INTO verse VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           ((edition, revision, *astuple(row)) for row in rows))
    aliases = {
        (normalize(alias), row.book_code)
        for row in rows
        for alias in (row.book_code, row.book_name, row.source_book_code)
    }
    connection.executemany("INSERT OR IGNORE INTO alias VALUES (?,?)", sorted(aliases))
    counts = connection.execute(
        """SELECT count(DISTINCT book_code),
                  (SELECT count(*) FROM (SELECT DISTINCT book_code, chapter_number
                     FROM verse WHERE edition=? AND revision=?)), count(*)
           FROM verse WHERE edition=? AND revision=?""",
        (edition, revision, edition, revision),
    ).fetchone()
    if counts != (66, 1189, 31102):
        raise ValueError(f"Unexpected {edition} bundle coverage: {counts}")
    return {"edition_id": edition, "revision": revision, "source_sha256": source_hash,
            "books": counts[0], "chapters": counts[1], "verses": counts[2]}


def build(kjv, bes, output):
    if output.exists():
        raise FileExistsError(output)
    manifest, kjv_rows, _ = load_pinned_kjv(kjv)
    bes_rows = load_bes(bes, kjv_rows)
    with TemporaryDirectory(dir=output.parent) as working:
        temporary = Path(working) / "scripture.sqlite"
        with closing(sqlite3.connect(temporary)) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(SCHEMA)
            artifact = manifest["artifact"]
            editions = [
                add_edition(connection, LOCAL, kjv_rows, "en", artifact["source_url"],
                            artifact["sha256"], "KJV scope validated for dev. Serving rights pending."),
                add_edition(connection, BES, bes_rows, "es", BES_URL, BES["dataset_revision"],
                            BES_RIGHTS),
            ]
            connection.execute("INSERT OR IGNORE INTO alias VALUES ('psalm','PSA')")
            if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise ValueError("SQLite integrity check failed")
        temporary.rename(output)
    with output.open("rb") as data:
        checksum = file_digest(data, "sha256").hexdigest()
    return {"bundle_sha256": checksum, "bytes": output.stat().st_size,
            "bes_xml_sha256": BES_XML_HASH, "editions": editions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kjv", type=Path)
    parser.add_argument("bes", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.kjv, args.bes, args.output), indent=2))


if __name__ == "__main__":
    main()
