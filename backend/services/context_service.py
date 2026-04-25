# backend/services/context_service.py

from typing import List, Optional
from backend.models.query_models import VerseItem

# Import metadata (adjust import paths if needed)
from backend.core.bible_metadata import BIBLE_BOOK_ORDER
from backend.core.bible_context_scenes import BIBLE_CONTEXT_SCENES
# TEMP: Chapter metadata not available in current phase
BIBLE_CHAPTER_METADATA = {}

def generate_free_context(verses: List[VerseItem]) -> Optional[str]:
    """
    Generate Free Context (Phase 1)
    - Deterministic
    - Scripture-anchored
    - No interpretation
    """

    if not verses:
        return None

    first_verse = verses[0]
    book = extract_book_name(first_verse.reference)
    chapter = first_verse.chapter

    print(f"[DEBUG] book={book}, chapter={chapter}, reference={first_verse.reference}")

    # ------------------------------------------------------------
    # Scene Context Lookup (Phase 1 Enhancement)
    # ------------------------------------------------------------
    # Extract chapter from reference if missing
    if not chapter and first_verse.reference:
        try:
            chapter = int(first_verse.reference.split()[1].split(":")[0])
        except Exception:
            chapter = None

    scene_key = f"{book}_{chapter}" if chapter else None

    if scene_key and scene_key in BIBLE_CONTEXT_SCENES:
        return BIBLE_CONTEXT_SCENES[scene_key]

    book_context = get_book_context(book)
    chapter_context = get_chapter_context(book, chapter)

    # Compose natural flow
    context_parts = []

    if book_context:
        context_parts.append(book_context)

    if chapter_context:
        context_parts.append(chapter_context)

    return " ".join(context_parts) if context_parts else None


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def extract_book_name(reference: str) -> str:
    """
    Extract book name from reference like 'John 3:16'
    """
    parts = reference.split()
    return parts[0] if parts else ""


def get_book_context(book: str) -> Optional[str]:
    """
    Retrieve book-level context
    """
    data = BIBLE_BOOK_ORDER.get(book)
    if not data:
        return None

    _, testament = data

    if testament == "OT":
        return f"This passage is from the Old Testament book of {book}, part of the earlier writings that record God's covenant and dealings with His people."
    elif testament == "NT":
        return f"This passage is from the New Testament book of {book}, which records the life, teachings, and continuing work surrounding Jesus and the early church."

    return None

def get_chapter_context(book: str, chapter: Optional[int]) -> Optional[str]:
    """
    Retrieve chapter-level context
    """
    if not chapter:
        return None

    key = f"{book}_{chapter}"
    data = BIBLE_CHAPTER_METADATA.get(key)

    if not data:
        return None

    return data.get("context")  # expected field
    