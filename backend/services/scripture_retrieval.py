"""Development retrieval from the verified local OSIS or the opt-in ASV adapter."""
from functools import lru_cache
import os
from pathlib import Path
import re

import requests

from backend.models.query_models import VerseItem
from backend.services.scripture_selection import LOCAL
from tools.scripture.import_kjv import load_pinned_kjv


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
    return re.sub(r"[^a-z0-9]", "", book.casefold())


def local_verses(reference):
    path = os.getenv("BTA_DEV_KJV_OSIS")
    if not path:
        raise ScriptureError("source_unavailable")
    try:
        aliases, chapters = local_index(path)
    except (OSError, ValueError) as exc:
        raise ScriptureError("source_unavailable") from exc

    match = re.fullmatch(r"(.+?)\s*(\d+)(?::(\d+)(?:\s*[-–]\s*(?:(\d+):)?(\d+))?)?", reference.strip())
    if not match:
        raise ScriptureError("missing_passage")
    book, chapter, verse, last_chapter, last_verse = match.groups()
    code = aliases.get(normalize(book))
    first_chapter, end_chapter = int(chapter), int(last_chapter or chapter)
    first, last = int(verse or 1), int(last_verse or verse or 0)
    if not code or first_chapter < 1 or first < 1 or end_chapter < first_chapter:
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
                                params={"translation": "asv"}, timeout=10)
        if response.status_code == 404:
            raise ScriptureError("missing_passage")
        response.raise_for_status()
        data = response.json()
        if data.get("translation_id") != "asv":
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
        return local_verses(reference)
    return external_verses(reference)
