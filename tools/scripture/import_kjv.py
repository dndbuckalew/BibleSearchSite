"""Validate the pinned KJV source and export rows for isolated dev staging."""

import argparse
from collections import Counter
import csv
from dataclasses import astuple, dataclass
import hashlib
import io
import json
from pathlib import Path
import re
from xml.sax import make_parser
from xml.sax.handler import ContentHandler, feature_namespaces


MANIFEST_SHA256 = "84c09445ebb552f399afb060b3df74ecb7617ffab1695f79b006353af936511b"
OSIS = "http://www.bibletechnologies.net/2003/OSIS/namespace"
REFERENCE = re.compile(r"([^.\s]+)\.([0-9]+)\.([0-9]+)")


@dataclass(frozen=True)
class Book:
    code: str
    name: str
    order: int


@dataclass(frozen=True)
class Verse:
    source_reference: str
    source_book_code: str
    source_chapter_label: str
    source_verse_label: str
    book_code: str
    book_name: str
    book_order: int
    chapter_number: int
    verse_order: int
    verse_label: str
    verse_text: str


@dataclass
class OpenVerse:
    marker: str
    reference: str
    code: str
    chapter: str
    label: str
    chunks: list[str]


def verified_bytes(path, expected_hash, expected_size=None):
    data = path.read_bytes()
    if (
        hashlib.sha256(data).hexdigest() != expected_hash.lower()
        or (expected_size is not None and len(data) != expected_size)
    ):
        raise ValueError(f"Input integrity check failed: {path.name}")
    return data


class VerseHandler(ContentHandler):
    def __init__(self, included, excluded):
        self.included = included
        self.excluded = excluded
        self.active = None
        self.addresses = set()
        self.markers = set()
        self.chapters = set()
        self.books = Counter()
        self.orders = Counter()
        self.rows = []

    def startElementNS(self, name, qname, attrs):
        if name != (OSIS, "verse"):
            return
        opening = attrs.get((None, "sID"))
        closing = attrs.get((None, "eID"))
        if bool(opening) == bool(closing):
            raise ValueError("Expected exactly one verse milestone marker")
        if opening:
            if self.active:
                raise ValueError("Overlapping verse milestone")
            reference = attrs.get((None, "osisID"), "")
            match = REFERENCE.fullmatch(reference)
            if not match:
                raise ValueError(f"Invalid source reference: {reference}")
            code, chapter, label = match.groups()
            if code not in self.included and code not in self.excluded:
                raise ValueError(f"Unknown book code: {code}")
            address = (code, int(chapter), int(label))
            if min(address[1:]) < 1:
                raise ValueError(f"Invalid source reference: {reference}")
            if address in self.addresses or opening in self.markers:
                raise ValueError(f"Duplicate verse reference or milestone: {reference}")
            self.addresses.add(address)
            self.markers.add(opening)
            self.chapters.add(address[:2])
            self.books[code] += 1
            self.active = OpenVerse(opening, reference, code, chapter, label, [])
            return

        verse = self.active
        if verse is None or closing != verse.marker:
            raise ValueError(f"Unmatched closing verse milestone: {closing}")
        self.active = None
        if verse.code in self.excluded:
            return

        text = "".join(verse.chunks)
        if not text.strip():
            raise ValueError(f"Empty verse: {verse.reference}")
        book = self.included[verse.code]
        chapter_number = int(verse.chapter)
        key = (book.code, chapter_number)
        self.orders[key] += 1
        self.rows.append(Verse(
            verse.reference, verse.code, verse.chapter, verse.label,
            book.code, book.name, book.order, chapter_number, self.orders[key],
            str(int(verse.label)), text,
        ))

    def characters(self, content):
        if self.active:
            self.active.chunks.append(content)

    def endDocument(self):
        if self.active:
            raise ValueError(f"Unclosed verse milestone: {self.active.reference}")


def parse_osis(source, included, excluded):
    if included.keys() & excluded or len({book.code for book in included.values()}) != len(included):
        raise ValueError("Ambiguous book map")
    handler = VerseHandler(included, excluded)
    parser = make_parser()
    parser.setFeature(feature_namespaces, True)
    parser.setContentHandler(handler)
    parser.parse(source)
    excluded_books = excluded & handler.books.keys()
    counts = {
        "source": {
            "books": len(handler.books),
            "chapters": len(handler.chapters),
            "verse_ids": len(handler.addresses),
        },
        "serving": {
            "books": len({row.book_code for row in handler.rows}),
            "chapters": len(handler.orders),
            "verse_ids": len(handler.rows),
        },
        "excluded": {
            "books": len(excluded_books),
            "verse_ids": sum(handler.books[book] for book in excluded_books),
        },
    }
    return handler.rows, counts


def load_pinned_kjv(source):
    manifest_path = Path(__file__).with_name("kjv-manifest.json")
    manifest = json.loads(verified_bytes(manifest_path, MANIFEST_SHA256))
    artifact = manifest["artifact"]
    raw = verified_bytes(source, artifact["sha256"], artifact["file_bytes"])
    mapping = manifest["book_mapping"]
    included = {
        row["source_book_code"]: Book(row["book_code"], row["book_name"], row["source_order"])
        for row in mapping["included"]
    }
    excluded = set(mapping["excluded"])
    if len(included) != len(mapping["included"]) or len(excluded) != len(mapping["excluded"]):
        raise ValueError("Duplicate source book code in manifest")
    rows, counts = parse_osis(io.BytesIO(raw), included, excluded)
    if counts != manifest["expected"]:
        raise ValueError(f"Unexpected source inventory: {counts}")

    return manifest, rows, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Pinned local OSIS file")
    parser.add_argument("output", type=Path, help="New staging CSV file")
    parser.add_argument("--batch-id", required=True, type=int)
    args = parser.parse_args()
    if args.batch_id < 1:
        parser.error("batch ID must be positive")

    manifest, rows, counts = load_pinned_kjv(args.source)
    artifact = manifest['artifact']

    with args.output.open("x", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerows((args.batch_id, number, *astuple(row)) for number, row in enumerate(rows, 1))
    print(json.dumps({
        "manifest_sha256": MANIFEST_SHA256,
        "source_sha256": artifact["sha256"],
        "source_bytes": artifact["file_bytes"],
        "inventory": counts,
    }, indent=2))


if __name__ == "__main__":
    main()
