"""
Reflection Engine
Phase 9.1D.2 — Controlled Reflection Generator (Enhanced)

Purpose
-------
Generate reflection prompts that invite the reader to engage
with Scripture after reading the summary.

The reflection layer asks:

    "What do you notice or think about as you read?"

This layer must never interpret scripture or direct personal action.

Design Strategy — Pattern Recognition
-------------------------------------
The engine detects the type of passage being read
(narrative, teaching, promise, wisdom, prayer).

It then selects a reflection prompt appropriate to
that passage type.

This improves the reader experience without violating
constitutional guardrails.

Governance Constraints
----------------------
• Single sentence
• Single question
• Non-interpretive
• No counseling tone
• Deterministic logic only

Constitutional Authorities
--------------------------
Phase 9.8 Governance Charter
Reflection Depth Bound
Persona Expression Ceiling
Non-Cross-Pollination Doctrine
"""

from typing import List, Optional


# ---------------------------------------------------------
# Base Reflection Templates (Scope-Based)
# ---------------------------------------------------------

REFLECTION_TEMPLATES = {

    "single_verse":
        "As you read this verse, what word or phrase draws your attention?",

    "verse_range":
        "Reading these verses together, what line or idea stays with you?",

    "full_chapter":
        "After reading this chapter, what moment or idea remains on your mind?",

    "multi_chapter":
        "Across these chapters, what pattern or theme begins to emerge as you read?",

    "nql_topic":
        "Looking across these passages on this topic, what thought comes to mind first?",

    "mixed_testament_topic":
        "Seeing these passages from different parts of Scripture together, what connection do you notice?"
}


# ---------------------------------------------------------
# Passage Type Reflection Templates
# ---------------------------------------------------------

PASSAGE_REFLECTIONS = {

    "narrative":
        "As you read this moment in the narrative, what detail stands out to you?",

    "teaching":
        "As you read this teaching, what phrase or idea stays with you?",

    "promise":
        "As you read this promise, what part of it draws your attention?",

    "wisdom":
        "As you consider this statement of wisdom, what thought comes to mind?",

    "prayer":
        "As you read this expression of prayer or praise, what words stand out to you?"
}


# ---------------------------------------------------------
# Reflection Fallback
# ---------------------------------------------------------

FALLBACK_REFLECTION = "As you read these verses, what stands out to you?"


# ---------------------------------------------------------
# Passage Pattern Detection
# ---------------------------------------------------------

TEACHING_PATTERNS = [
    "blessed",
    "whoever",
    "therefore",
    "let",
    "if"
]

PROMISE_PATTERNS = [
    "i will",
    "shall",
    "will not"
]

PRAYER_PATTERNS = [
    "o lord",
    "my soul",
    "i will praise"
]

WISDOM_PATTERNS = [
    "the wise",
    "the fool",
    "better than"
]

NARRATIVE_PATTERNS = [
    "went",
    "came",
    "said",
    "answered",
    "saw"
]


def _detect_passage_type(text: str) -> Optional[str]:

    text_lower = text.lower()

    for p in PRAYER_PATTERNS:
        if p in text_lower:
            return "prayer"

    for p in PROMISE_PATTERNS:
        if p in text_lower:
            return "promise"

    for p in TEACHING_PATTERNS:
        if p in text_lower:
            return "teaching"

    for p in WISDOM_PATTERNS:
        if p in text_lower:
            return "wisdom"

    for p in NARRATIVE_PATTERNS:
        if p in text_lower:
            return "narrative"

    return None


# ---------------------------------------------------------
# Constitutional Guard Validation
# ---------------------------------------------------------

def _validate_reflection(reflection: str) -> bool:
    """
    Ensures reflection prompt complies with constitutional constraints.

    Requirements:
    • exactly one question
    • single sentence
    """

    if not reflection:
        return False

    if reflection.count("?") != 1:
        return False

    if reflection.strip().count(".") > 1:
        return False

    return True


# ---------------------------------------------------------
# Reflection Generator
# ---------------------------------------------------------

def generate_reflection(verses: List, structural_scope: Optional[str]) -> str:

    try:

        # -------------------------------------------------
        # Structural reflection (primary logic)
        # -------------------------------------------------

        reflection = REFLECTION_TEMPLATES.get(structural_scope)

        if reflection and _validate_reflection(reflection):
            return reflection

        # -------------------------------------------------
        # Passage pattern reflection (single verse enhancement)
        # -------------------------------------------------

        if verses and structural_scope == "single_verse":

            verse_text = verses[0].text

            passage_type = _detect_passage_type(verse_text)

            if passage_type and passage_type in PASSAGE_REFLECTIONS:

                reflection = PASSAGE_REFLECTIONS[passage_type]

                if _validate_reflection(reflection):
                    return reflection

        return FALLBACK_REFLECTION

    except Exception:
        return FALLBACK_REFLECTION
    