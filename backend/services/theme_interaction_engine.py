"""
Theme Interaction Engine
Phase 9.1D.2.3 — Semantic Movement Engine

Purpose
-------
Transform detected motifs into meaningful semantic movements
that the Summary Expression Builder can compose into narrative
understanding.

Design Principle
----------------
Motifs reveal underlying movements within Scripture. Those
movements are expressed as ideas the reader can understand,
not as analytical labels.
"""

from typing import Dict, List, Optional


INTERACTION_MAP = {
    frozenset(["love", "sacrifice"]):
        "God's love is revealed through what He is willing to give.",

    frozenset(["love", "redemption"]):
        "God's love moves toward restoring what has been broken.",

    frozenset(["life", "redemption"]):
        "God's restoring work is meant to bring life where loss had entered.",

    frozenset(["fear", "faith"]):
        "Faith answers the instability that fear creates.",

    frozenset(["justice", "mercy"]):
        "God's justice does not erase mercy but holds both within His purpose.",

    frozenset(["creation", "life"]):
        "What God creates is meant to live and flourish under His authority.",

    frozenset(["promise", "redemption"]):
        "What God promises is directed toward redemption.",

    frozenset(["teaching", "wisdom"]):
        "Truth given by God is meant to shape the way life is lived.",
}


CENTRAL_CONCLUSION_MAP = {
    frozenset(["love", "sacrifice"]):
        "The depth of God's love is seen in what He is willing to give.",

    frozenset(["love", "redemption"]):
        "God's love is revealed through His work of restoring what has been lost.",

    frozenset(["creation", "life"]):
        "God stands as the source from whom life and the world itself begin.",

    frozenset(["fear", "faith"]):
        "Trust in God becomes the answer to fear.",

    frozenset(["justice", "mercy"]):
        "God's mercy does not deny justice but fulfills His purpose beyond it.",
}

def _normalize_themes(themes: List[str]) -> List[str]:

    cleaned = []
    seen = set()

    for theme in themes or []:

        value = theme.strip().lower()

        if not value or value in seen:
            continue

        cleaned.append(value)
        seen.add(value)

    return cleaned

def _build_supporting_movements(themes: List[str]) -> List[str]:

    movements = []

    for i in range(len(themes)):
        for j in range(i + 1, len(themes)):

            pair = frozenset([themes[i], themes[j]])

            if pair in INTERACTION_MAP:
                movements.append(INTERACTION_MAP[pair])

    return movements

def _build_central_conclusion(themes: List[str]) -> Optional[str]:

    for i in range(len(themes)):
        for j in range(i + 1, len(themes)):

            pair = frozenset([themes[i], themes[j]])

            if pair in CENTRAL_CONCLUSION_MAP:
                return CENTRAL_CONCLUSION_MAP[pair]

    return None

def interpret_theme_interactions(themes: List[str]) -> Dict[str, object]:

    normalized = _normalize_themes(themes)

    supporting_movements = _build_supporting_movements(normalized)

    central_conclusion = _build_central_conclusion(normalized)

    # --- Added: handle single motif passages ---

    return {
        "detected_motifs": normalized,
        "motif_relationships": [],
        "supporting_movements": supporting_movements,
        "central_conclusion": central_conclusion,
    } 
