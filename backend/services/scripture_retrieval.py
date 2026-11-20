"""Development retrieval from the verified local OSIS or the opt-in BSB adapter."""
from functools import lru_cache
import os
from pathlib import Path
import re
import unicodedata

import psycopg

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


def postgres_connection():
    return psycopg.connect(host="127.0.0.1", port=55441, dbname="postgres",
                           user="bta_scripture_test", connect_timeout=3)


def postgres_chapters(selection, book, first_chapter, end_chapter):
    try:
        with postgres_connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                """SELECT s.snapshot_id
                   FROM bta_scripture.snapshot s
                   JOIN bta_scripture.edition e USING (edition_id)
                   JOIN bta_scripture.import_batch b USING (batch_id)
                   WHERE e.edition_code = %s AND b.source_revision = %s""",
                (selection["edition_id"], selection["dataset_revision"]),
            )
            matches = cursor.fetchall()
            if len(matches) != 1:
                raise ScriptureError("source_unavailable")
            snapshot = matches[0][0]
            cursor.execute("SELECT DISTINCT book_code, book_name, source_book_code FROM bta_scripture.snapshot_book")
            aliases = {}
            for code, name, source in cursor:
                for alias in (code, name, source):
                    aliases.setdefault(normalize(alias), set()).add(code)
            codes = aliases.get(normalize(book), set())
            if len(codes) != 1:
                raise ScriptureError("missing_passage")
            code = next(iter(codes))
            cursor.execute(
                """SELECT source_reference, book_code, book_name, book_order, chapter_number,
                          verse_order, verse_label, verse_text
                   FROM bta_scripture_api.passage_render_v1
                   WHERE snapshot_id = %s AND book_code = %s AND chapter_number BETWEEN %s AND %s
                   ORDER BY chapter_number, verse_order""",
                (snapshot, code, first_chapter, end_chapter),
            )
            chapters = {}
            for ref, code, name, order, chapter, position, label, verse_text in cursor:
                row = Verse(ref, code, str(chapter), label, code, name, order, chapter, position, label, verse_text)
                chapters.setdefault((code, chapter), []).append(row)
            return code, chapters
    except psycopg.Error as exc:
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
    if os.getenv("BTA_DEV_SCRIPTURE_POSTGRES") == "1":
        code, chapters = postgres_chapters(selection, book, first_chapter, end_chapter)
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
    rows = [
        row
        for number in range(first_chapter, end_chapter + 1)
        for row in chapters.get((code, number), [])
        if (number != first_chapter or int(row.verse_label) >= first)
        and (number != end_chapter or not last or int(row.verse_label) <= last)
    ]
    if not rows or (verse and int(rows[0].verse_label) != first) or (last and int(rows[-1].verse_label) != last):
        raise ScriptureError("missing_passage")
    return [
        VerseItem(reference=f"{row.book_name} {row.chapter_number}:{row.verse_label}",
                  text=row.verse_text.strip(), book_order=row.book_order,
                  chapter=row.chapter_number, verse=int(row.verse_label),
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
