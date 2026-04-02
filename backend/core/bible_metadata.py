"""
BTA — Canonical Bible Metadata Authority
Phase 9.1A.1 — Canonical Metadata Isolation (Structural Hygiene)

Constitutional Classification:
- Structural Refactor
- No Behavior Change
- No Feature Expansion
- Drift-Sensitive

Purpose:
This module centralizes canonical Bible ordering metadata
previously embedded inside query_service.py.

IMPORTANT:
The data structure below MUST remain identical to the
original implementation (dictionary mapping of:

    Book Name -> (Canonical Order Number, Testament)

No schema mutation permitted in this phase.
"""

# ------------------------------------------------------------------
# Canonical Bible Book Order — KJV Authority
# Structure preserved exactly from original service implementation
# ------------------------------------------------------------------

BIBLE_BOOK_ORDER = {
    # Old Testament
    "Genesis": (1, "OT"),
    "Exodus": (2, "OT"),
    "Leviticus": (3, "OT"),
    "Numbers": (4, "OT"),
    "Deuteronomy": (5, "OT"),
    "Joshua": (6, "OT"),
    "Judges": (7, "OT"),
    "Ruth": (8, "OT"),
    "1 Samuel": (9, "OT"),
    "2 Samuel": (10, "OT"),
    "1 Kings": (11, "OT"),
    "2 Kings": (12, "OT"),
    "1 Chronicles": (13, "OT"),
    "2 Chronicles": (14, "OT"),
    "Ezra": (15, "OT"),
    "Nehemiah": (16, "OT"),
    "Esther": (17, "OT"),
    "Job": (18, "OT"),
    "Psalms": (19, "OT"),
    "Proverbs": (20, "OT"),
    "Ecclesiastes": (21, "OT"),
    "Song of Solomon": (22, "OT"),
    "Isaiah": (23, "OT"),
    "Jeremiah": (24, "OT"),
    "Lamentations": (25, "OT"),
    "Ezekiel": (26, "OT"),
    "Daniel": (27, "OT"),
    "Hosea": (28, "OT"),
    "Joel": (29, "OT"),
    "Amos": (30, "OT"),
    "Obadiah": (31, "OT"),
    "Jonah": (32, "OT"),
    "Micah": (33, "OT"),
    "Nahum": (34, "OT"),
    "Habakkuk": (35, "OT"),
    "Zephaniah": (36, "OT"),
    "Haggai": (37, "OT"),
    "Zechariah": (38, "OT"),
    "Malachi": (39, "OT"),

    # New Testament
    "Matthew": (40, "NT"),
    "Mark": (41, "NT"),
    "Luke": (42, "NT"),
    "John": (43, "NT"),
    "Acts": (44, "NT"),
    "Romans": (45, "NT"),
    "1 Corinthians": (46, "NT"),
    "2 Corinthians": (47, "NT"),
    "Galatians": (48, "NT"),
    "Ephesians": (49, "NT"),
    "Philippians": (50, "NT"),
    "Colossians": (51, "NT"),
    "1 Thessalonians": (52, "NT"),
    "2 Thessalonians": (53, "NT"),
    "1 Timothy": (54, "NT"),
    "2 Timothy": (55, "NT"),
    "Titus": (56, "NT"),
    "Philemon": (57, "NT"),
    "Hebrews": (58, "NT"),
    "James": (59, "NT"),
    "1 Peter": (60, "NT"),
    "2 Peter": (61, "NT"),
    "1 John": (62, "NT"),
    "2 John": (63, "NT"),
    "3 John": (64, "NT"),
    "Jude": (65, "NT"),
    "Revelation": (66, "NT"),
}
