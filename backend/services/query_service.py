from typing import List, Optional, Tuple
import requests

from backend.models.query_models import VerseItem, QueryRequest, QueryResponse
from backend.config.feature_flags import FEATURE_FLAGS

BIBLE_API_BASE = "https://bible-api.com"

# --------------------------------------------------------------
# Canonical Bible book order (OT → NT)
# --------------------------------------------------------------
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


class QueryService:
    """
    Phase 7.x Query Service

    Responsibilities:
    - Accept explicit verse input OR natural-language questions
    - Resolve scripture deterministically
    - Apply canonical OT → NT ordering
    - Return Scripture + Context + Reflection
    """

    # ------------------------------------------------------------------
    # Parse canonical metadata
    # ------------------------------------------------------------------
    def _parse_reference_metadata(self, reference: str):
        for book, (order, testament) in BIBLE_BOOK_ORDER.items():
            if reference.startswith(book):
                return order, testament
        return None, None

    # ------------------------------------------------------------------
    # Detect explicit verse reference
    # ------------------------------------------------------------------
    def _is_explicit_verse(self, question: str) -> bool:
        q = question.strip()

        if ":" in q:
            return True

        for book in BIBLE_BOOK_ORDER.keys():
            if q.startswith(book):
                return True

        return False

    # ------------------------------------------------------------------
    # Split multi-topic questions conservatively
    # ------------------------------------------------------------------
    def _extract_topics(self, question: str) -> List[str]:
        normalized = question.lower().strip()

        if " and " in normalized:
            parts = normalized.split(" and ")
        elif " or " in normalized:
            parts = normalized.split(" or ")
        elif "," in normalized:
            parts = normalized.split(",")
        else:
            return [question.strip()]

        topics = []
        for p in parts:
            t = p.strip()
            if t and t not in topics:
                topics.append(t)

        return topics if topics else [question.strip()]

    # ------------------------------------------------------------------
    # Resolve NQL to anchor scriptures (deterministic)
    # ------------------------------------------------------------------
    def _resolve_nql_to_scripture(self, question: str) -> List[str]:
        q = question.lower()

        if "suffering" in q or "pain" in q:
            return ["Romans 8:18", "Psalm 34:19"]

        if "fear" in q or "anxiety" in q:
            return ["Isaiah 41:10", "Philippians 4:6-7"]

        if "forgive" in q or "forgiveness" in q:
            return ["Matthew 18:21-22", "Ephesians 4:32"]

        if "purpose" in q:
            return ["Jeremiah 29:11", "Ephesians 2:10"]

        # Safe fallback
        return ["Psalm 119:105", "John 1:5"]

    # ------------------------------------------------------------------
    # Fetch scripture from API
    # ------------------------------------------------------------------
    def fetch_single_verse(
        self,
        reference: str,
        translation: str = "kjv"
    ) -> Optional[VerseItem]:

        try:
            url = f"{BIBLE_API_BASE}/{requests.utils.quote(reference)}"
            params = {"translation": translation}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            text = ""
            if "text" in data:
                text = data["text"].strip()
            elif "verses" in data:
                text = " ".join(v.get("text", "") for v in data["verses"]).strip()

            if not text:
                return None

            reference_label = data.get("reference", "").strip() or reference
            book_order, testament = self._parse_reference_metadata(reference_label)

            return VerseItem(
                reference=reference_label,
                text=text,
                book_order=book_order,
                testament=testament
            )

        except Exception:
            return None

    # ------------------------------------------------------------------
    # Main query entry point (Phase 7.6+)
    # ------------------------------------------------------------------
    def process_query(self, req: QueryRequest) -> QueryResponse:

        if FEATURE_FLAGS.get("FORCE_SAFE_MODE", False):
            return QueryResponse(
                verses=[],
                summary="The system is currently operating in safe mode.",
                commentary=""
            )

        verse_items: List[VerseItem] = []
        question = req.question.strip()

        # Explicit verse vs NQL routing
        if self._is_explicit_verse(question):
            topics = self._extract_topics(question)
            for topic in topics:
                verse = self.fetch_single_verse(
                    reference=topic,
                    translation=req.translation or "kjv"
                )
                if verse:
                    verse_items.append(verse)
        else:
            anchors = self._resolve_nql_to_scripture(question)
            for ref in anchors:
                verse = self.fetch_single_verse(
                    reference=ref,
                    translation=req.translation or "kjv"
                )
                if verse:
                    verse_items.append(verse)

        # Canonical ordering
        verse_items.sort(
            key=lambda v: (
                v.testament != "OT",
                v.book_order or 999
            )
        )

        # Deterministic Context + Reflection
        context_text = (
            "These passages are connected by a shared theme found across Scripture, "
            "showing continuity in how the Bible addresses this question."
        )

        reflection_text = (
            "This reflection is offered as an invitation for inward consideration. "
            "You are not expected to respond, but to quietly consider how these passages "
            "shape your understanding."
        )

        return QueryResponse(
            verses=verse_items,
            summary=context_text,
            commentary=reflection_text
        )
