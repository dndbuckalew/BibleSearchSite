"""Read pinned local Scripture or the opt-in hosted BSB comparison."""
from contextlib import closing
from functools import lru_cache
from hashlib import file_digest
import os
from pathlib import Path
import re
import unicodedata

import sqlite3

import requests

from backend.models.query_models import VerseItem
from backend.services.scripture_selection import LOCAL
from tools.scripture.import_kjv import Verse, load_pinned_kjv


class ScriptureError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


@lru_cache(maxsize=1)
def local_index(path):
    manifest, rows, _ = load_pinned_kjv(Path(path))
    if manifest["artifact"]["source_revision"] != LOCAL["dataset_revision"]:
        raise ValueError("Unexpected KJV dataset revision")
    aliases = {}
    chapters = {}
    for row in rows:
        for alias in (row.book_name, row.book_code, row.source_book_code):
            aliases[normalize(alias)] = row.book_code
        chapters.setdefault((row.book_code, row.chapter_number), []).append(row)
    return aliases, chapters


def normalize(book):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", book.casefold()))


@lru_cache(maxsize=8)
def verify_bundle(path, checksum, stamp):
    with path.open("rb") as data:
        if file_digest(data, "sha256").hexdigest() != checksum:
            raise ScriptureError("source_unavailable")


def sqlite_connection():
    filename = os.getenv("BTA_SCRIPTURE_SQLITE_PATH")
    checksum = os.getenv("BTA_SCRIPTURE_SQLITE_SHA256", "").lower()
    if not filename or not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ScriptureError("source_unavailable")
    path = Path(filename).resolve()
    stat = path.stat()
    verify_bundle(path, checksum, (stat.st_mtime_ns, stat.st_size, stat.st_ino))
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)


def sqlite_catalog():
    """Advertise added editions only from the configured, verified bundle."""
    try:
        with closing(sqlite_connection()) as connection:
            if not connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='edition_catalog'"
            ).fetchone():
                return []
            rows = connection.execute(
                """SELECT snapshot.edition, snapshot.revision, edition_catalog.label
                   FROM snapshot JOIN edition_catalog USING (edition)
                   ORDER BY snapshot.edition"""
            ).fetchall()
    except (OSError, sqlite3.Error, ScriptureError):
        return []
    return [
        {"option_id": f"local-{edition}", "edition_id": edition, "source_id": "local",
         "edition_label": title, "source_label": "Local Scripture dataset",
         "dataset_revision": revision}
        for edition, revision, title in rows
    ]


def normalize_edition_alias(book):
    return "".join(char for char in unicodedata.normalize("NFKD", book.casefold())
                   if char.isalnum())


def sqlite_chapters(selection, book, first_chapter, end_chapter):
    identity = (selection["edition_id"], selection["dataset_revision"])
    try:
        with closing(sqlite_connection()) as connection:
            if connection.execute(
                "SELECT 1 FROM snapshot WHERE edition=? AND revision=?", identity
            ).fetchone() is None:
                raise ScriptureError("source_unavailable")
            if selection["edition_id"] in {"kjv", "bes"}:
                codes = connection.execute(
                    "SELECT book_code FROM alias WHERE alias_key=?", (normalize(book),)
                ).fetchall()
            else:
                codes = connection.execute(
                    "SELECT book_code FROM edition_alias WHERE edition=? AND alias_key=?",
                    (selection["edition_id"], normalize_edition_alias(book)),
                ).fetchall()
            if len(codes) != 1:
                raise ScriptureError("missing_passage")
            code = codes[0][0]
            rows = connection.execute(
                """SELECT source_reference,source_book_code,source_chapter_label,
                          source_verse_label,book_code,book_name,book_order,chapter_number,
                          verse_order,verse_label,verse_text
                   FROM verse WHERE edition=? AND revision=? AND book_code=?
                       AND chapter_number BETWEEN ? AND ?
                   ORDER BY chapter_number, verse_order""",
                (*identity, code, first_chapter, end_chapter),
            )
            chapters = {}
            for values in rows:
                verse = Verse(*values)
                chapters.setdefault((code, verse.chapter_number), []).append(verse)
            return code, chapters
    except (OSError, sqlite3.Error) as exc:
        raise ScriptureError("source_unavailable") from exc


def local_verses(reference, selection=LOCAL):
    match = re.fullmatch(r"(.+?)\s*(\d+)(?::(\d+)(?:\s*[-–]\s*(?:(\d+):)?(\d+))?)?", reference.strip())
    if not match:
        raise ScriptureError("missing_passage")
    book, chapter, verse, last_chapter, last_verse = match.groups()
    first_chapter, end_chapter = int(chapter), int(last_chapter or chapter)
    first, last = int(verse or 1), int(last_verse or verse or 0)
    if first_chapter < 1 or first < 1 or end_chapter < first_chapter:
        raise ScriptureError("missing_passage")
    if os.getenv("BTA_SCRIPTURE_SQLITE_PATH"):
        code, chapters = sqlite_chapters(selection, book, first_chapter, end_chapter)
    else:
        if selection != LOCAL:
            raise ScriptureError("source_unavailable")
        path = os.getenv("BTA_DEV_KJV_OSIS")
        if not path:
            raise ScriptureError("source_unavailable")
        try:
            aliases, chapters = local_index(path)
        except (OSError, ValueError) as exc:
            raise ScriptureError("source_unavailable") from exc

        code = aliases.get(normalize(book))
        if not code:
            raise ScriptureError("missing_passage")

    if (code, first_chapter) not in chapters or (code, end_chapter) not in chapters:
        raise ScriptureError("missing_passage")
    def bounds(row):
        start, _, end = row.verse_label.partition("-")
        return int(start), int(end or start)

    rows = [
        row
        for number in range(first_chapter, end_chapter + 1)
        for row in chapters.get((code, number), [])
        if (number != first_chapter or bounds(row)[1] >= first)
        and (number != end_chapter or not last or bounds(row)[0] <= last)
    ]
    if (not rows or (verse and not bounds(rows[0])[0] <= first <= bounds(rows[0])[1])
            or (last and not bounds(rows[-1])[0] <= last <= bounds(rows[-1])[1])):
        raise ScriptureError("missing_passage")
    return [
        VerseItem(reference=f"{row.book_name} {row.chapter_number}:{row.verse_label}",
                  text=row.verse_text.strip(), book_order=row.book_order,
                  chapter=row.chapter_number, verse=bounds(row)[0],
                  testament="OT" if row.book_order <= 39 else "NT")
        for row in rows
    ]


def external_verses(reference):
    try:
        response = requests.get(f"https://bible-api.com/{requests.utils.quote(reference, safe='')}",
                                params={"translation": "bsb"}, timeout=10)
        if response.status_code == 404:
            raise ScriptureError("missing_passage")
        response.raise_for_status()
        data = response.json()
        if data.get("translation_id") != "bsb":
            raise ScriptureError("edition_unverified")
        verses = [
            VerseItem(reference=f"{row['book_name']} {row['chapter']}:{row['verse']}",
                      text=row["text"].strip(), chapter=row["chapter"], verse=row["verse"])
            for row in data["verses"]
        ]
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ScriptureError("source_unavailable") from exc
    if not verses or any(not verse.text for verse in verses):
        raise ScriptureError("missing_passage")
    return verses


def retrieve(reference, selection):
    if selection["source_id"] == "local":
        return local_verses(reference, selection)
    return external_verses(reference)
