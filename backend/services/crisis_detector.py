# backend/services/crisis_detector.py

from typing import Optional, Tuple


# ------------------------------------------------------------
# Tier 0 — Deterministic Crisis Patterns
# Structural only. No interpretation.
# ------------------------------------------------------------
CRISIS_PATTERNS = {
    "self_harm_signal": [
        "kill myself",
        "want to die",
        "end my life",
        "suicide",
        "self harm",
        "hurt myself",
        "no reason to live",
    ],
    "hopelessness_signal": [
        "no hope",
        "life is pointless",
        "nothing matters",
        "give up on life",
    ],
}


def detect_crisis(question: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Tier 0 — Deterministic structural crisis detection.

    Returns:
        (crisis_detected, crisis_type, confidence)

    No LLM.
    No sentiment scoring.
    No expressive language.
    No routing decisions.
    """

    if not question:
        return False, None, None

    normalized = question.lower()

    for crisis_type, phrases in CRISIS_PATTERNS.items():
        for phrase in phrases:
            if phrase in normalized:
                return True, crisis_type, "high"

    return False, None, None
