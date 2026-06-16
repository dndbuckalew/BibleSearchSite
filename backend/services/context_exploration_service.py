from typing import List, Dict

from backend.models.query_models import VerseItem
from backend.services.ai_client import call_ai_model


def generate_context_exploration(
    verses: List[VerseItem],
    resolved_meaning: str = "",
    supporting_movements: List[str] | None = None,
) -> str | None:
    """
    Dynamic Context Exploration.

    Uses the resolved Scripture set and already-authorized
    understanding to render deeper contextual circumstances.

    This does not create a second understanding authority.
    """

    if not verses:
        return None

    if supporting_movements is None:
        supporting_movements = []

    circumstance_prompt = _build_circumstance_prompt(
        verses=verses,
        resolved_meaning=resolved_meaning,
        supporting_movements=supporting_movements,
    )

    try:
        result = call_ai_model(circumstance_prompt)
        cleaned = (result or "").strip()

        if cleaned:
            return cleaned

    except Exception as e:
        print("CONTEXT EXPLORATION ERROR:", str(e))

    return _fallback_context_exploration(verses)


def _build_circumstance_prompt(
    verses: List[VerseItem],
    resolved_meaning: str,
    supporting_movements: List[str],
) -> str:
    verse_lines = _format_verses_for_prompt(verses)

    movements = "\n".join(
        f"- {movement}" for movement in supporting_movements if movement
    )

    return f"""
You are rendering Dynamic Context for a Bible reader.

Your role is to help the reader understand the circumstances surrounding the resolved Scripture set.

Use the already-resolved meaning as an anchor.

Do NOT create new meaning.
Do NOT preach.
Do NOT moralize.
Do NOT create doctrine.
Do NOT write commentary.
Do NOT list facts mechanically.
Do NOT expose labels such as who, what, when, where, how.
Do NOT mention architecture, themes, discovery, facts, or rendering.
Do NOT say "these passages present" or "these passages participate."

Goal:
Help the reader picture the circumstances surrounding the Scripture.

Render:
- Natural paragraphs
- Helper persona tone
- Circumstances with enough detail to understand what is happening
- People, setting, situation, tension, and relationships when supported
- A closing paragraph that gently brings the contextual picture together

Keep it bounded:
- One exploration response only
- No follow-up questions
- No invitation to continue
- No verse hopping
- No additional references unless already present in the resolved Scripture set

SCRIPTURE SET:
{verse_lines}

RESOLVED MEANING ANCHOR:
{resolved_meaning}

SUPPORTING MOVEMENTS:
{movements}

Write the Dynamic Context response now.
"""


def _format_verses_for_prompt(
    verses: List[VerseItem],
) -> str:
    lines = []

    for verse in verses:
        reference = verse.reference or ""
        text = verse.text or ""

        if reference and text:
            lines.append(f"{reference} — {text}")
        elif reference:
            lines.append(reference)

    return "\n".join(lines)


def _fallback_context_exploration(
    verses: List[VerseItem],
) -> str | None:
    book_groups = _group_references_by_book(verses)

    if not book_groups:
        return None

    if len(book_groups) <= 1:
        book = next(iter(book_groups.keys()))
        return (
            "Looking a little more closely, the surrounding circumstances "
            f"in {book} help explain what is happening in this passage. "
            "Paying attention to who is involved, what is taking place, "
            "and what situation surrounds the passage can help the reader "
            "see the moment more clearly."
        )

    return (
        "Looking a little more closely, the subject appears in different "
        "circumstances across the selected Scriptures. Some settings involve "
        "instruction, others involve community life, hardship, encouragement, "
        "or spiritual growth. Seeing those circumstances together helps the "
        "reader understand how the subject appears in real situations and "
        "relationships within Scripture."
    )


def _group_references_by_book(
    verses: List[VerseItem],
) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}

    for verse in verses:
        reference = verse.reference or ""
        book = _extract_book_name(reference)

        if not book:
            continue

        groups.setdefault(book, [])

        if reference and reference not in groups[book]:
            groups[book].append(reference)

    return groups


def _extract_book_name(reference: str) -> str:
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
    