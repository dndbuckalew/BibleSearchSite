"""Normalize the pinned BES USFX source into the shared verse shape."""
from hashlib import sha256
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

from backend.services.scripture_selection import BES
from tools.scripture.import_kjv import Verse, verified_bytes

BES_URL = "https://ebible.org/Scriptures/spabes_usfx.zip"
BES_XML_HASH = "ec27f6a90f41b3a988dc6260ea8870c60e51d91fbe7a787d9581e499e131a339"
BES_RIGHTS = "https://ebible.org/spabes/copyright.htm"


def load_bes(path, kjv_rows):
    data = verified_bytes(path, BES["dataset_revision"])
    with ZipFile(BytesIO(data)) as archive:
        raw = archive.read("spabes_usfx.xml")
        if sha256(raw).hexdigest() != BES_XML_HASH:
            raise ValueError("Unexpected BES XML hash")
        names = {
            row.attrib["code"]: row.attrib["long"]
            for row in ElementTree.fromstring(archive.read("BookNames.xml")).findall("book")
        }
        source = ElementTree.fromstring(raw)
    canon = {row.book_code: row.book_order for row in kjv_rows}
    if source.tag != "usfx" or source.findtext("languageCode") != "spa" or names.keys() != canon.keys():
        raise ValueError("Unexpected BES language or book mapping")
    rows, addresses = [], set()
    chapters, books = set(), set()

    for book in source.findall("book"):
        code = book.attrib["id"]
        if code not in canon or code in books:
            raise ValueError(f"Unknown or duplicate BES book: {code}")
        books.add(code)
        chapter = label = None
        chunks = None
        order = 0

        def visit(node):
            nonlocal chapter, label, chunks, order
            if node.tag == "c":
                if chunks is not None:
                    raise ValueError("Chapter boundary inside a BES verse")
                chapter = node.attrib["id"]
                key = (code, int(chapter))
                if key in chapters:
                    raise ValueError(f"Duplicate BES chapter: {key}")
                chapters.add(key)
                order = 0
            elif node.tag == "v":
                label = node.attrib["id"]
                address = (code, int(chapter), int(label))
                if chunks is not None or address in addresses or node.attrib["bcv"] != f"{code}.{chapter}.{label}":
                    raise ValueError(f"Invalid or duplicate BES start: {address}")
                addresses.add(address)
                chunks = []
            elif node.tag == "ve":
                if chunks is None or not "".join(chunks).strip():
                    raise ValueError("Unmatched or empty BES verse")
                order += 1
                rows.append(Verse(f"{code}.{chapter}.{label}", code, chapter, label, code,
                                  names[code], canon[code], int(chapter), order, str(int(label)),
                                  "".join(chunks)))
                chunks = None
            if chunks is not None and node.text:
                chunks.append(node.text)
            for child in node:
                visit(child)
                if chunks is not None and child.tail:
                    chunks.append(child.tail)

        visit(book)
        if chunks is not None:
            raise ValueError(f"Unclosed BES verse in {code}")
    if (len(books), len(chapters), len(rows)) != (66, 1189, 31102):
        raise ValueError("Unexpected BES coverage")
    return rows
