import hashlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from import_kjv import Book, parse_osis, verified_bytes


def milestones(reference, text="Text", end=None):
    return (
        f'<verse sID="{reference}" osisID="{reference}"/>{text}'
        f'<verse eID="{end or reference}"/>'
    )


class ImportTests(unittest.TestCase):
    def parse(self, content):
        return parse_osis(
            io.BytesIO(f'<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">{content}</osis>'.encode()),
            {"Gen": Book("GEN", "Genesis", 1)},
            {"Tob"},
        )

    def test_integrity(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixture"
            path.write_bytes(b"abc")
            digest = hashlib.sha256(b"abc").hexdigest()
            self.assertEqual(verified_bytes(path, digest, 3), b"abc")
            with self.assertRaisesRegex(ValueError, "integrity"):
                verified_bytes(path, digest, 4)
            path.write_bytes(b"abd")
            with self.assertRaisesRegex(ValueError, "integrity"):
                verified_bytes(path, digest, 3)

    def test_unknown_code(self):
        with self.assertRaisesRegex(ValueError, "Unknown book code"):
            self.parse(milestones("GSYS.1.1"))

    def test_ambiguous_book_map(self):
        book = Book("GEN", "Genesis", 1)
        for included, excluded in [
            ({"Gen": book}, {"Gen"}),
            ({"Gen": book, "Alias": book}, set()),
        ]:
            with self.subTest(included=included, excluded=excluded):
                with self.assertRaisesRegex(ValueError, "Ambiguous book map"):
                    parse_osis(io.BytesIO(b""), included, excluded)

    def test_excluded_code(self):
        rows, counts = self.parse(milestones("Tob.1.1") + milestones("Gen.1.1"))
        self.assertEqual([row.source_reference for row in rows], ["Gen.1.1"])
        self.assertEqual(counts["excluded"], {"books": 1, "verse_ids": 1})

    def test_milestone_pairing(self):
        for content in [
            '<verse eID="Gen.1.1"/>',
            '<verse sID="Gen.1.1" osisID="Gen.1.1"/>',
            '<verse sID="Gen.1.1" osisID="Gen.1.1"/>' + milestones("Gen.1.2"),
            milestones("Gen.1.1", end="Gen.1.2"),
        ]:
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, "milestone"):
                self.parse(content)

    def test_duplicate_reference(self):
        for duplicate in ["Gen.1.1", "Gen.01.01"]:
            with self.subTest(duplicate=duplicate), self.assertRaisesRegex(ValueError, "Duplicate"):
                self.parse(milestones("Gen.1.1") + milestones(duplicate))

    def test_order_labels_and_inline_text(self):
        rows, _ = self.parse(
            milestones("Gen.1.2", " Before <q>a <hi>nested</hi> tag</q>, after. ")
            + milestones("Gen.1.10")
            + milestones("Gen.2.1")
        )
        self.assertEqual([row.verse_order for row in rows], [1, 2, 1])
        self.assertEqual([row.verse_label for row in rows], ["2", "10", "1"])
        self.assertEqual([row.chapter_number for row in rows], [1, 1, 2])
        self.assertEqual(rows[0].verse_text, " Before a nested tag, after. ")
        self.assertEqual(rows[0].source_reference, "Gen.1.2")
