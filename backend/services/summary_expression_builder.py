"""
Summary Expression Builder
Phase 9.1D.2.7 — Final Expression Enhancement

Purpose
-------
Generate the Summary Expression that helps the reader understand
the meaning emerging from a passage of Scripture.

Design Principles
-----------------
- Let Scripture determine the music
- Activate meaning into movement
- Preserve multi-faceted unity
- Avoid paraphrasing the verse
- Maintain thoughtful reflective tone
- Reveal deeper meaning without verbosity
"""

from typing import List, Tuple
from dataclasses import dataclass
import random


@dataclass
class ThemeInteractionResult:
    """
    Canonical semantic object produced by the Theme Interaction Engine.
    """

    query_type: str
    translation: str
    passage_reference: str
    passage_text: str

    detected_motifs: List[str]
    motif_relationships: List[Tuple[str, str]]

    central_conclusion: str
    supporting_movements: List[str]


class SummaryExpressionBuilder:
    """
    Builds the Summary Expression from a ThemeInteractionResult.

    Narrative Flow
    --------------
    Meaning → Movement → Forward Direction (not closure)
    """

    def build_summary(self, result: ThemeInteractionResult) -> str:
        """
        Public entry point for generating the summary.
        """

        print("SUMMARY BUILDER HIT")  # DEBUG LINE

        anchor = self._clean_fragment(result.central_conclusion)

        primary = self._detect_primary_movement(result)
        primary = self._clean_fragment(primary)

        supporting = self._select_supporting_movements(
            result.supporting_movements, primary
        )

        opening = self._build_opening(anchor, primary)

        development = self._build_development(anchor, supporting)

        summary = " ".join([p for p in [opening, development] if p])

        return self._finalize_summary(summary)

    def _detect_primary_movement(self, result: ThemeInteractionResult) -> str:
        if result.supporting_movements:
            return result.supporting_movements[0]
        return result.central_conclusion

    def _build_opening(self, anchor: str, primary: str) -> str:
        """
        Enter directly into meaning — no labels, no templates.
        """

        if primary and primary.lower() != anchor.lower():
            return primary

        return anchor

    def _build_development(self, anchor: str, supporting: List[str]) -> str:
        """
        Create forward movement using natural connective language.
        This is where "life" is introduced.
        """

        if not supporting:
            return ""

        movement = supporting[0]
        movement = self._clean_fragment(movement)

        if not movement:
            return ""

        connectors = [
            "as the passage moves toward",
            "revealing that",
            "pointing toward",
            "showing that",
            "as it begins to unfold toward",
            "carrying this forward toward",
        ]

        connector = random.choice(connectors)

        return f"{connector} {movement}"

    def _select_supporting_movements(
        self, movements: List[str], primary_movement: str
    ) -> List[str]:

        selected: List[str] = []

        for movement in movements[1:]:
            cleaned = self._clean_fragment(movement)

            if not cleaned:
                continue

            if cleaned.lower() == primary_movement.strip().lower():
                continue

            selected.append(cleaned)

            if len(selected) >= 1:
                break

        return selected

    def _clean_fragment(self, text: str) -> str:
        if not text:
            return ""

        cleaned = " ".join(text.strip().split())

        return cleaned.strip()

    def _finalize_summary(self, summary: str) -> str:
        cleaned = " ".join(summary.strip().split())

        if not cleaned:
            return ""

        if cleaned[-1] not in ".!?":
            cleaned = f"{cleaned}."

        return cleaned
