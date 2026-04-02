"""
AI Summary Service
Phase 9.1D.2.1

Purpose
-------
Provide an AI-assisted summary layer that can later connect
to an LLM while preserving deterministic fallback behavior.

Design Principles
-----------------
• Safe: never replaces deterministic fallback
• Controlled: prompt generation bounded by guardrails
• Optional: operates even when no LLM is connected
• Expandable: future AI integration requires minimal change

Execution Flow
--------------
summary_engine
      ↓
generate_ai_summary()
      ↓
LLM client (future)
      ↓
None → deterministic summary fallback
"""

from typing import List, Optional


# ---------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------
def build_ai_summary_prompt(
    verses,
    structural_scope: str,
    signals: List[str]
) -> str:
    """
    Build a controlled prompt for AI summarization.

    This prompt will be used by an LLM client once integrated.
    """

    verse_text = " ".join(v.text for v in verses if v.text)

    signal_text = ", ".join(signals) if signals else "none"

    prompt = f"""
You are assisting a reader in understanding Scripture.

Your role is to explain what the passage is communicating.

Rules:
- Do not repeat the verse
- Do not preach
- Do not invent theology
- Do not speculate beyond the text
- Focus only on meaning expressed in the passage

Verse Text:
{verse_text}

Structural Scope:
{structural_scope}

Detected Linguistic Signals:
{signal_text}

Task:
Provide a short summary explaining the meaning of the passage.
Maximum two sentences.
"""

    return prompt.strip()


# ---------------------------------------------------------
# Deterministic AI Fallback (Used When LLM Exists But Fails)
# ---------------------------------------------------------
def _generate_signal_based_summary(signals: List[str]) -> Optional[str]:
    """
    Produce a semantic summary based on communication role
    signals when an LLM response is unavailable.

    This is only used when an LLM exists but returns no output.
    """

    if not signals:
        return None

    primary = signals[0].lower()

    if primary == "promise":
        return (
            "This passage expresses a promise revealing how God acts toward humanity "
            "and invites the reader to trust in what God provides."
        )

    if primary == "blessing":
        return (
            "This passage declares a blessing that highlights the kind of heart "
            "God honors and invites reflection on spiritual humility."
        )

    if primary == "instruction":
        return (
            "This passage provides guidance about how life should be lived "
            "in response to God's will."
        )

    if primary == "warning":
        return (
            "This passage cautions the reader about the consequences "
            "of turning away from God's ways."
        )

    if primary == "narrative":
        return (
            "This passage records an event within the unfolding story "
            "of Scripture that reveals something about God's work."
        )

    if primary == "creation":
        return (
            "This passage describes the beginning of God's creative work "
            "and introduces the foundation of the biblical narrative."
        )

    if primary == "teaching":
        return (
            "This passage communicates a teaching intended to shape how "
            "the reader understands life before God."
        )

    return None


# ---------------------------------------------------------
# Main AI Summary Generator
# ---------------------------------------------------------
def generate_ai_summary(
    verses,
    structural_scope: str,
    signals: List[str],
    llm_client=None
) -> Optional[str]:
    """
    Generate a summary using AI if available.

    Behavior
    --------
    1. If no LLM client → return None (deterministic summary runs)
    2. If LLM exists → generate AI summary
    3. If LLM fails → signal-based semantic fallback
    """

    try:

        if not verses:
            return None

        # -------------------------------------------------
        # NO LLM CONNECTED → deterministic summary fallback
        # -------------------------------------------------

        if llm_client is None:
            return None

        # -------------------------------------------------
        # LLM Path (Future Integration)
        # -------------------------------------------------

        prompt = build_ai_summary_prompt(
            verses,
            structural_scope,
            signals
        )

        response = llm_client.generate(prompt)

        if response:
            return response.strip()

        # -------------------------------------------------
        # LLM exists but returned nothing → signal fallback
        # -------------------------------------------------

        return _generate_signal_based_summary(signals)

    except Exception:
        return None
          