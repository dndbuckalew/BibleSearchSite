# backend/services/context_service.py

from typing import List, Optional
from backend.models.query_models import VerseItem

# Import metadata (adjust import paths if needed)
from backend.core.bible_metadata import BIBLE_BOOK_ORDER



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
    data = BIBLE_BOOK_METADATA.get(book)
    if not data:
        return None

    return data.get("context")  # expected field


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
    