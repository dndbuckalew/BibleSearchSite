 # backend/services/reflection_service.py

from backend.services.summary_expression_builder import ThemeInteractionResult
from backend.services.crisis_detector import detect_crisis


class ReflectionService:
    """
    Reflection Service (Hands Layer)

    Produces a reflective prompt grounded in the result,
    while remaining non-instructional and non-theological.
    """

    def build_reflection(self, result: ThemeInteractionResult) -> str:

        # --------------------------------------------------
        # 0. CRISIS FAIL-SAFE
        # --------------------------------------------------
        # NOTE:
        # Crisis detection is handled upstream in the query layer.
        # Reflection must not perform crisis detection to avoid
        # false positives from scripture or generated meaning.

        # --------------------------------------------------
        # 1. VALIDATION
        # --------------------------------------------------
        if not result:
            return ""

        core = (getattr(result, "central_conclusion", "") or "").strip()

        if not core:
            core = (getattr(result, "passage_text", "") or "").strip()

        if not core:
            return ""

        movements = getattr(result, "supporting_movements", []) or []

        # --------------------------------------------------
        # 2. BUILD COMPONENTS
        # --------------------------------------------------
        opening = self._build_opening(core)
        anchor = self._build_anchor(core)
        awareness = self._build_awareness(core, movements)
        question = self._build_reflection_question(core, movements)

        # --------------------------------------------------
        # 3. ASSEMBLY
        # --------------------------------------------------
        parts = [opening, anchor, awareness, question]
        reflection = " ".join([p for p in parts if p]).strip()

        # --------------------------------------------------
        # 4. FINAL VALIDATION
        # --------------------------------------------------
        if not reflection.endswith("?"):
            reflection = reflection.rstrip(".") + "?"

        return reflection

    def _build_opening(self, core: str) -> str:
        return "At times, something in this may begin to surface in a quiet way."

    def _build_anchor(self, core: str) -> str:
        return f"This seems to reflect something about {core.lower()}."

    def _build_awareness(self, core: str, movements: list[str]) -> str:
        if movements:
            return "Sometimes this begins to take shape quietly, before you fully recognize it."
        return "Sometimes this becomes noticeable in ways that are easy to overlook."

    def _build_reflection_question(self, core: str, movements: list[str]) -> str:
        return "Where do you sense this touching your own life right now?"   

