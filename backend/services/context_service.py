from typing import List, Optional
from backend.models.query_models import VerseItem

from backend.core.bible_metadata import BIBLE_BOOK_ORDER
from backend.core.bible_context_scenes import BIBLE_CONTEXT_SCENES
from backend.services.ai_client import call_ai_model # adjust if needed

from backend.services.dynamic_context_service import (
    is_broad_scope,
    generate_dynamic_context,
)
from backend.core.context_theme_registry import CONTEXT_THEME_REGISTRY

# Phase 3.2.1:
# Chapter-level orientation layer not yet populated.
# Reserved for progressive widening (Part 1, Layer 2).
BIBLE_CHAPTER_METADATA = {}


def generate_free_context(verses: List[VerseItem]) -> Optional[str]:

    if not verses:
        return None

    if is_broad_scope(verses):
        return generate_dynamic_context(verses)

    return generate_local_context(verses)


def generate_local_context(verses: List[VerseItem]) -> Optional[str]:
    """
    Local Context (Part 1)
    Progressive widening resolution:
    1. nearest local scene
    2. chapter-level orientation
    3. broader book-level orientation
    4. generic fallback (last resort)
    """
    if not verses:
        return None

    first_verse = verses[0]
    book = extract_book_name(first_verse.reference)
    chapter = first_verse.chapter

    if not chapter and first_verse.reference:
        try:
            chapter = int(first_verse.reference.split()[1].split(":")[0])
        except Exception:
            chapter = None

    scene_key = f"{book}_{chapter}" if chapter else None
    scene_context = BIBLE_CONTEXT_SCENES.get(scene_key) if scene_key else None
    chapter_context = get_chapter_context(book, chapter)
    book_context = get_book_context(book)

    # Layer 1 — nearest local scene
    if scene_context:
        return render_context_frame(scene_context)

    # Layer 2 — chapter-level orientation
    if chapter_context:
        return render_context_frame(chapter_context)

    # Layer 3 — broader book-level orientation
    if book_context:
        return render_context_frame(book_context)

    # Layer 4 — generic fallback
    return render_context_frame(get_generic_fallback(book))

def generate_dynamic_context(verses: List[VerseItem]) -> Optional[str]:
    """
    Broad-scope Context fallback.

    Used when multiple books or contextual environments
    participate within the resolved passage set.

    This remains deterministic, bounded, and non-interpretive.
    """

    if not verses:
        return None

    books = []
    seen = set()

    for verse in verses:
        book = extract_book_name(verse.reference or "")

        if book and book not in seen:
            books.append(book)
            seen.add(book)

    if not books:
        return None

    if len(books) == 1:
        context_frame = (
            f"This passage draws from multiple portions of the book of "
            f"{books[0]}, reflecting related Scriptural continuity "
            f"within that surrounding context."
        )
    elif len(books) == 2:
        context_frame = (
            f"These passages draw from both {books[0]} and {books[1]}, "
            f"bringing together related Scriptural moments that "
            f"participate within a broader continuity of Scripture."
        )
    else:
        joined = ", ".join(books[:-1]) + f", and {books[-1]}"

        context_frame = (
            f"These passages draw from multiple areas of Scripture "
            f"including {joined}. Together they provide a broader "
            f"context for understanding why this subject appears "
            f"throughout Scripture."
        )

    rendered_context = render_context_frame(context_frame)

    if not rendered_context:
        return None

    return rendered_context
    
# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def extract_book_name(reference: str) -> str:
    """
    Extract canonical book name from reference like:
    'John 3:16', '1 John 3:1', 'Song of Solomon 2:1'
    """
    if not reference:
        return ""

    parts = reference.split()

    if len(parts) >= 2 and parts[0].isdigit():
        return f"{parts[0]} {parts[1]}"

    if len(parts) >= 3 and parts[0].lower() == "song" and parts[1].lower() == "of":
        return "Song of Solomon"

    return parts[0]

def get_book_context(book: str) -> Optional[str]:
    """
    Retrieve book-level context (Layer 3)

    Must ALWAYS return a minimal deterministic frame if book exists.
    """

    if not book:
        return None

    data = BIBLE_BOOK_ORDER.get(book)

    # 🔒 Guaranteed fallback — even if metadata lookup fails
    if not data:
        return f"This passage comes from the book of {book}."

    _, testament = data

    if testament == "OT":
        return f"This passage comes from the Old Testament book of {book}, part of the earlier scriptural record of God’s dealings with His people."
    elif testament == "NT":
        return f"This passage comes from the New Testament book of {book}, written to guide and address believers in their understanding and life."

    # Final safety fallback
    return f"This passage comes from the book of {book}."

def get_chapter_context(book: str, chapter: Optional[int]) -> Optional[str]:
    """
    Retrieve chapter-level orientation (Layer 2)
    """
    if not chapter:
        return None

    key = f"{book}_{chapter}"
    data = BIBLE_CHAPTER_METADATA.get(key)

    if not data:
        return None

    return data.get("context")

def get_participating_context_themes() -> str:
    """
    Phase 2.2

    Temporary registry-driven participating
    context theme list.

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

def render_context_frame(context_frame: Optional[str]) -> Optional[str]:
    """
    Hybrid rendering boundary (Part 1)

    Deterministic Context selects the approved contextual frame.
    LLM enriches expression WITHOUT adding meaning or interpretation.
    """
    
    if context_frame is None:
        return None

    prompt = f"""
You are rendering CONTEXT for a Bible passage.

Your role is ONLY to improve how the context is expressed so the reader can better understand what is happening in the surrounding moment.

STRICT RULES:
- Do NOT explain meaning
- Do NOT interpret doctrine
- Do NOT teach or instruct
- Do NOT analyze the passage
- Do NOT expand beyond what is already described
- Do NOT introduce historical reconstruction or external facts

You may:
- Clarify what is happening
- Improve readability
- Make the scene more natural and understandable
- Slightly rephrase for better flow

Focus only on:
"What is happening here and what surrounding situation helps explain it?"

Context Frame:
{context_frame}

Return ONLY the improved contextual description.
"""
    try:
        result = call_ai_model(prompt)
        return result.strip() if result else context_frame
    except Exception:
        return context_frame

def get_generic_fallback(book: str) -> Optional[str]:
    """
    Generic fallback (Layer 4, last resort only)
    """
    if not book:
        return None

    return f"This passage comes from the book of {book}."

