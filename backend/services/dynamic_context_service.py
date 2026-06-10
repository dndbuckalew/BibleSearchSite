from typing import List, Optional

from backend.models.query_models import VerseItem
from backend.core.context_theme_registry import CONTEXT_THEME_REGISTRY


def is_broad_scope(verses: List[VerseItem]) -> bool:
    """
    Scope router for Dynamic Context.

    Broad scope is detected when the resolved passage set contains
    multiple distinct books or multiple distinct chapters.

    This prevents multi-passage results from anchoring
    only to the first resolved verse.
    """

    if not verses or len(verses) <= 1:
        return False

    books = set()
    chapters = set()

    for verse in verses:
        reference = verse.reference or ""
        book = extract_book_name(reference)

        chapter = verse.chapter

        if not chapter and reference:
            try:
                left_side = reference.split(":")[0]
                chapter = int(left_side.split()[-1])
            except Exception:
                chapter = None

        if book:
            books.add(book)

        if chapter:
            chapters.add((book, chapter))

    return len(books) > 1 or len(chapters) > 1


def generate_dynamic_context(
    verses: List[VerseItem]
) -> Optional[str]:
    """
    Dynamic Context Overview.

    Temporary implementation.

    Future phases will replace this with:
    - Participation decomposition
    - Dynamic Context Overview
    - Explore Further
    """

    return None


def get_participating_context_themes() -> str:
    """
    Temporary registry-driven theme participation.

    Future:
    PostgreSQL Context Theme Registry
    """

    themes = [
        theme["theme_name"]
        for theme in CONTEXT_THEME_REGISTRY
        if theme.get("enabled")
    ]

    if not themes:
        return ""

    return (
        "\n\nParticipating Context Themes:\n"
        + "\n".join(f"• {theme}" for theme in themes)
    )


def extract_book_name(reference: str) -> str:
    """
    Extract canonical book name from reference.
    """

    if not reference:
        return ""

    parts = reference.split()

    if len(parts) >= 2 and parts[0].isdigit():
        return f"{parts[0]} {parts[1]}"

    if (
        len(parts) >= 3
        and parts[0].lower() == "song"
        and parts[1].lower() == "of"
    ):
        return "Song of Solomon"

    return parts[0]
    