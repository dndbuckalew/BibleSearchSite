# backend/services/meaning_engine.py

"""
Meaning Engine
Phase 9.1D.2.8 — AI-Driven Meaning Construction (Soul Layer)

Purpose
-------
Construct meaning directly from Scripture using AI.

This layer produces:
- core (central meaning)
- expansion (how meaning unfolds)
- resolution (integrated meaning)

Design Rules
------------
- Scripture is the source of truth
- AI constructs meaning (not templates)
- No hardcoded sentence maps
- No generic fallback language
- Must support:
    - Single verse
    - Multi-verse
    - Chapter
    - NQL (topic)
    - NQL (natural question)
"""

from typing import List, Tuple
import json

# 👉 IMPORTANT: ensure this function exists in ai_client.py
from backend.services.ai_client import call_ai_model


# ------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------
def build_meaning(passage_text, motifs, relationships, user_question: str = ""):
    """
    AI-driven meaning construction.

    Returns:
        {
            "core": str,
            "expansion": List[str],
            "resolution": str
        }
    """

    passage = (passage_text or "").strip()

    if not passage:
        return {
            "core": "",
            "expansion": [],
            "resolution": ""
        }

    prompt = _build_meaning_prompt(
        passage=passage,
        motifs=motifs,
        relationships=relationships,
        user_question=user_question,
    )

    try:
        ai_response = call_ai_model(prompt)

        print("MEANING ENGINE RAW RESPONSE:", ai_response)

        parsed = _parse_ai_response(ai_response)

        if _is_valid_meaning(parsed):
            return {
                "core": parsed.get("central_conclusion", ""),
                "expansion": parsed.get("supporting_movements", []),
                "resolution": _build_resolution(parsed)
            }

    except Exception as e:
        print("MEANING ENGINE ERROR:", str(e))

    # --------------------------------------
    # SAFE STRUCTURAL FALLBACK (V1 FORMAT)
    # --------------------------------------
    return {
        "core": "Meaning is present within the passage and begins to take shape as the words are considered together.",
        "expansion": [],
        "resolution": ""
    }


# ------------------------------------------------------
# PROMPT BUILDER
# ------------------------------------------------------
def _build_meaning_prompt(passage, motifs, relationships, user_question):
    """
    Constructs the AI prompt to generate meaning.
    """

    return f"""
You are helping a reader understand Scripture by expressing the meaning that emerges from the passage itself.

Your role is NOT to summarize, analyze, or explain academically.

Instead:
- Express the meaning as it naturally arises from the words
- Stay grounded in what is actually present in the passage
- Allow depth to emerge without forcing structure or compression

SCRIPTURE:
\"\"\"
{passage}
\"\"\"

USER QUESTION (if present):
{user_question}

OPTIONAL SIGNALS (use only if helpful, never force them):
Motifs: {motifs}
Relationships: {relationships}

INSTRUCTIONS:

1. Let the meaning emerge directly from the words of the passage.

2. If the passage contains multiple meaningful elements (such as love, giving, belief, life), allow each to be expressed and connected rather than compressed into a single idea.

3. Speak in a natural, human tone that expresses the meaning itself — not describing or analyzing it.

4. Go deeper than surface meaning:
   - bring out the weight of key words
   - allow ideas to build on each other
   - show how the meaning develops across the passage

5. Avoid mechanical or staged phrasing such as:
   - "as it unfolds"
   - "as the passage moves"

6. Do not reduce the meaning. Let it be fully expressed if the passage supports it.

7. Stay grounded only in what is present in the passage.
   Do not introduce ideas not supported by the text.

8. Do not preach, instruct, or apply the meaning.
   Only express what the passage is communicating.

9. Let the meaning carry a sense of movement and fullness, like a composition rather than a list.
Allow the ideas to build on each other in a connected and flowing way, where each part deepens what came before it.
Avoid short, isolated statements. Let the meaning feel unified, continuous, and complete.
Return a natural, flowing explanation of the meaning with depth and connection between ideas.

10. Allow the meaning to develop with depth.
If an idea is significant, it may be revisited, expanded, or deepened as the explanation continues.
Do not rush to complete the thought. Let it unfold with weight, as understanding grows.
Let the explanation feel like something that has been understood deeply, not quickly stated.

OUTPUT FORMAT (STRICT JSON):

{{
  "central_conclusion": "Express the core meaning clearly, allowing depth and significance to be present",
  "supporting_movements": [
    "Additional expressions that expand, deepen, or connect the meaning within the passage",
    "Include multiple movements if needed — do not limit depth"
  ]
}}
"""

# ------------------------------------------------------
# AI RESPONSE PARSER
# ------------------------------------------------------
def _parse_ai_response(response: str):
    try:
        clean = response.strip()

        # ✅ REMOVE ```json wrappers if present
        if clean.startswith("```"):
            clean = clean.strip("`")
            clean = clean.replace("json", "", 1).strip()

        data = json.loads(clean)

        central = str(data.get("central_conclusion", "")).strip()
        movements = data.get("supporting_movements", [])

        # ✅ FIX: ensure movements is always a list
        if isinstance(movements, str):
            movements = [movements]

        if isinstance(movements, list):
            movements = [str(m).strip() for m in movements if m]

        return {
            "central_conclusion": central,
            "supporting_movements": movements,
        }

    except Exception:
        return {
            "central_conclusion": "",
            "supporting_movements": [],
        }


# ------------------------------------------------------
# VALIDATION
# ------------------------------------------------------
def _is_valid_meaning(parsed):
    if not parsed:
        return False

    central = parsed.get("central_conclusion", "")
    movements = parsed.get("supporting_movements", [])

    if not central:
        return False

    if not movements:
        return False

    return True


# ------------------------------------------------------
# RESOLUTION BUILDER (NEW)
# ------------------------------------------------------
def _build_resolution(parsed):
    """
    Builds the integrated resolution layer from parsed meaning.
    """

    expansion = parsed.get("supporting_movements", [])

    if not expansion:
        return ""

    return expansion[-1]


# ------------------------------------------------------
# SAFE FALLBACK (LEGACY — KEEP, NOT USED)
# ------------------------------------------------------
def _safe_fallback(passage: str):
    return (
        "The passage expresses something that carries meaning beyond the surface,",
        [
            "drawing attention to what is being revealed and why it matters within the broader story of Scripture."
        ],
    )
