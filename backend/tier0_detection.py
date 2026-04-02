 # backend/tier0_detection.py
from __future__ import annotations

from backend.core.vocabulary.crisis_vocabulary import KEYWORDS_BY_CRISIS_TYPE

from dataclasses import dataclass
from typing import Optional


# -------------------------------------------------------------------
# Tier 0 Output Contract (LOCKED)
# -------------------------------------------------------------------
@dataclass(frozen=True)
class Tier0Result:
    crisis_type: Optional[str]
    confidence: float  # deterministic, bounded 0.0–1.0


# -------------------------------------------------------------------
# Deterministic Confidence Settings (LOCKED MECHANICS)
# -------------------------------------------------------------------
# Confidence is computed deterministically based on keyword hits:
#   confidence = min(1.0, total_hits / HIT_SATURATION)
#
# This is NOT probabilistic.
# It is a bounded scaling factor.
HIT_SATURATION = 3  # 1 hit=0.33, 2 hits=0.67, 3+ hits=1.0


def _normalize(text: str) -> str:
    """
    Deterministic normalization only.
    No LLM. No semantic expansion.
    """
    return " ".join((text or "").lower().strip().split())


def detect_tier0(user_text: str) -> Tier0Result:
    """
    Tier 0 deterministic detection:
    - keyword-based matching against KEYWORDS_BY_CRISIS_TYPE
    - returns (crisis_type, confidence)
    - does NOT block execution
    - does NOT generate language
    """

    normalized = _normalize(user_text)

    if not normalized:
        return Tier0Result(crisis_type=None, confidence=0.0)

    best_type: Optional[str] = None
    best_hits = 0

    for crisis_type, keywords in KEYWORDS_BY_CRISIS_TYPE.items():
        if not keywords:
            continue

        hits = 0

        for kw in keywords:
            k = _normalize(kw)
            if not k:
                continue

            # Deterministic substring match (simple + stable)
            if k in normalized:
                hits += 1

        # Choose crisis type with highest hit count
        # Stable tie-breaking (Python dict order)
        if hits > best_hits:
            best_hits = hits
            best_type = crisis_type

    confidence = 0.0
    if best_hits > 0:
        confidence = min(1.0, best_hits / float(HIT_SATURATION))

    return Tier0Result(crisis_type=best_type, confidence=confidence)
       