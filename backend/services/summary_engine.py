"""
Summary Engine
Phase 9.1D.1 — Controlled Summary Generation (Rewritten)

Purpose
-------
Provide orientation for the reader before reflection.

The Summary layer answers:

    "What kind of passage is this and what is happening here?"

It must NOT:
• repeat the verse
• interpret theology
• give devotional instruction

Instead, it describes the *type of passage* or *event occurring*.

Design Strategy — Pattern Reduction
-----------------------------------
The engine uses deterministic pattern reduction:

1. Remove filler language
2. Detect passage type patterns
3. Extract a simplified event phrase
4. Produce a descriptive orientation sentence

This allows the system to summarize any verse without
hardcoding specific scripture knowledge.

This layer supports the reflective pipeline:

Scripture → Summary → Reflection
"""

# ---------------------------------------------------------
# Phase 9.1D.2.1 — Universal Linguistic Framework
# ---------------------------------------------------------

from backend.core.linguistic.linguistic_patterns import (
    combine_verse_text,
    detect_linguistic_patterns,
)

# ---------------------------------------------------------
# Phase 9.1D.2.1 — AI Summary Service
# ---------------------------------------------------------

from backend.services.ai_summary_service import generate_ai_summary

# ---------------------------------------------------------
# Phase 9.1D.2.3 — Theme Interaction Engine
# (REGISTERED ONLY — NOT YET USED)
# ---------------------------------------------------------

from backend.services.theme_interaction_engine import interpret_theme_interactions


DEFAULT_FALLBACK = (
    "This passage presents a statement within the broader narrative of Scripture."
)


# ---------------------------------------------------------
# Sentence Limiter
# ---------------------------------------------------------
def _limit_sentences(text: str, max_sentences: int = 3) -> str:

    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    limited = sentences[:max_sentences]

    if not limited:
        return DEFAULT_FALLBACK

    return ". ".join(limited) + "."


# ---------------------------------------------------------
# Detect OT / NT mixture
# ---------------------------------------------------------
def _detect_testament_mix(verses) -> bool:

    OT_BOOKS = {
        "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges",
        "Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles",
        "Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes",
        "Song","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel",
        "Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk",
        "Zephaniah","Haggai","Zechariah","Malachi"
    }

    NT_BOOKS = {
        "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
        "Galatians","Ephesians","Philippians","Colossians","1 Thessalonians",
        "2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews",
        "James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
    }

    ot_found = False
    nt_found = False

    for verse in verses:

        ref = verse.reference.split(" ")[0]

        if ref in OT_BOOKS:
            ot_found = True

        if ref in NT_BOOKS:
            nt_found = True

    return ot_found and nt_found


# ---------------------------------------------------------
# NEW: Linguistic Signal Summary Generator
# ---------------------------------------------------------
def _generate_signal_summary(primary, secondary):

    if not primary:
        return None

    primary = primary.lower()

    if primary == "blessing":
        return "This passage declares a blessing while also teaching about the condition of the human heart before God."

    if primary == "promise":
        return "This passage expresses a promise revealing how God acts toward humanity."

    if primary == "instruction":
        return "This passage provides instruction intended to guide how life should be lived before God."

    if primary == "warning":
        return "This passage cautions the reader about the consequences of turning away from God's ways."

    if primary == "creation":
        return "This passage describes the beginning of God's creative work and introduces the foundation of the biblical narrative."

    if primary == "narrative":
        return "This passage records an event within the unfolding story of Scripture."

    if primary == "teaching":
        return "This passage communicates a teaching intended to shape how the reader understands life before God."

    return None


# ---------------------------------------------------------
# Pattern Reduction — Passage Type Detection
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
    "will not",
    "i am with"
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

EVENT_PATTERNS = {
    "baptized": "the baptism described in this verse",
    "created": "the beginning of creation",
    "born": "a birth described within the narrative",
    "rose": "a resurrection event described in the passage",
    "called": "a moment of calling within the narrative",
    "gave": "an act of giving described in the verse",
    "loved": "an expression of love described in the passage"
}


def _detect_passage_type(text: str) -> str:

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

    return "statement"


def _detect_event_phrase(text: str):

    text_lower = text.lower()

    for key, phrase in EVENT_PATTERNS.items():
        if key in text_lower:
            return phrase

    return None


# ---------------------------------------------------------
# Generate Single Verse Summary
# ---------------------------------------------------------
def _summarize_single_verse(verse_text: str) -> str:

    passage_type = _detect_passage_type(verse_text)

    event_phrase = _detect_event_phrase(verse_text)

    if event_phrase:
        return f"This verse records {event_phrase}."

    if passage_type == "teaching":
        return "This verse presents a statement of teaching within the passage."

    if passage_type == "promise":
        return "This verse presents a statement of promise."

    if passage_type == "prayer":
        return "This verse expresses prayer or praise directed toward God."

    if passage_type == "wisdom":
        return "This verse presents a statement of wisdom about living."

    if passage_type == "narrative":
        return "This verse records an event within the narrative."

    return DEFAULT_FALLBACK


# ---------------------------------------------------------
# Main Summary Engine
# ---------------------------------------------------------
def generate_summary(verses, structural_scope: str, theme_analysis=None) -> str:

    try:

        if not verses:
            return DEFAULT_FALLBACK

        combined_text = combine_verse_text(verses)

        pattern_scores = detect_linguistic_patterns(combined_text)

        primary_pattern = None
        secondary_pattern = None

        if pattern_scores:
            primary_pattern = pattern_scores[0][0]

            if len(pattern_scores) > 1:
                secondary_pattern = pattern_scores[1][0]

        # -------------------------------------------------
        # NEW: Build top signals for AI summary attempt
        # -------------------------------------------------

        signals = []
        if primary_pattern:
            signals.append(primary_pattern)
        if secondary_pattern:
            signals.append(secondary_pattern)

        # -------------------------------------------------
        # Phase 9.1D.2.3 — Theme Interaction Engine
        # -------------------------------------------------

        if theme_analysis is None:
            theme_analysis = interpret_theme_interactions(signals)

        # -------------------------------------------------
        # NEW: AI-guided summary attempt
        # -------------------------------------------------

        from backend.services.ai_client import get_ai_client

        llm_client = get_ai_client()

        ai_summary = generate_ai_summary(
            verses=verses,
            structural_scope=structural_scope,
            signals=signals,
            llm_client=llm_client
        )    

        # -------------------------------------------------
        # Phase 9.1D.2.6 — Semantic Pipeline Priority
        # -------------------------------------------------

        if ai_summary:
            return ai_summary 

        return DEFAULT_FALLBACK

        # NOTE:
        # AI summary no longer short-circuits this engine.
        # Upstream logic in query_service.py now controls summary priority.

        # -------------------------------------------------
        # Theme Interaction Layer (Phase 9.1D.2.3)
        # -------------------------------------------------

        themes = []
        interactions = []
        central_theme = None

        if theme_analysis:
            themes = theme_analysis.get("themes", [])
            interactions = theme_analysis.get("interactions", [])
            central_theme = theme_analysis.get("central_theme")

        # -------------------------------------------------
        # Theme-driven summary
        # -------------------------------------------------

        if themes or interactions or central_theme:

            summary_parts = []

            if structural_scope == "single_verse":
                summary_parts.append(
                    "This passage presents a moment within the unfolding story of Scripture."
                )

            elif structural_scope == "verse_range":
                summary_parts.append(
                    "These verses form a connected passage that develops a shared theme within the chapter."
                )

            elif structural_scope == "full_chapter":
                summary_parts.append(
                    "This chapter develops a broader movement within the biblical narrative."
                )

            elif structural_scope == "multi_chapter":
                summary_parts.append(
                    "These passages span multiple chapters and together reveal a larger movement within Scripture."
                )

            else:
                summary_parts.append(
                    "This passage contributes to the broader story revealed throughout Scripture."
                )

            if themes:

                theme_sentence = "Within this passage themes of "

                if len(themes) == 1:
                    theme_sentence += f"{themes[0]} appear."

                elif len(themes) == 2:
                    theme_sentence += f"{themes[0]} and {themes[1]} appear."

                else:
                    theme_sentence += ", ".join(themes[:-1]) + f", and {themes[-1]} appear."

                summary_parts.append(theme_sentence)

            if interactions:
                summary_parts.append(interactions[0])

            if central_theme:
                summary_parts.append(central_theme)

            summary_text = " ".join(summary_parts)

            return _limit_sentences(summary_text, 5)

        # -------------------------------------------------
        # NEW: Signal-driven summary
        # -------------------------------------------------

        signal_summary = _generate_signal_summary(primary_pattern, secondary_pattern)

        if signal_summary:
            return _limit_sentences(signal_summary)

        mixed_testament = _detect_testament_mix(verses)

        if mixed_testament:

            text = (
                "These passages present a shared theme across both the Old "
                "and New Testament. Each verse contributes to a broader "
                "idea expressed across different parts of Scripture."
            )

            return _limit_sentences(text)

        if structural_scope == "single_verse":

            verse_text = verses[0].text

            text = _summarize_single_verse(verse_text)

            return _limit_sentences(text)

        if structural_scope == "verse_range":

            text = (
                "These verses form a short connected passage within the chapter. "
                "Together they describe a moment or teaching that develops "
                "across the selected lines."
            )

            return _limit_sentences(text)

        if structural_scope == "full_chapter":

            text = (
                "This chapter presents a larger section of the biblical narrative "
                "containing multiple connected passages. The verses together "
                "develop a central theme across the chapter."
            )

            return _limit_sentences(text)

        if structural_scope == "multi_chapter":

            text = (
                "These passages span multiple chapters within Scripture. "
                "Together they present events or teachings that develop "
                "across a broader portion of the biblical narrative."
            )

            return _limit_sentences(text)

        if structural_scope in {"nql_topic", "mixed_testament_topic"}:

            text = (
                "These passages are grouped around a shared theme found "
                "across Scripture. Each verse reflects that idea within "
                "its own context."
            )

            return _limit_sentences(text)

        return DEFAULT_FALLBACK

    except Exception:

        return DEFAULT_FALLBACK
        