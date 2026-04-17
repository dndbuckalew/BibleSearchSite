# backend/services/query_service.py

# Structural escalation router (Phase 9.8B.5)
from backend.escalation_router import route_escalation_level
from typing import List, Optional, Union, Any
import requests
import re
from fastapi import HTTPException

# Tier 0 Detection Import (Phase 9.8A)
from backend.tier0_detection import detect_tier0, Tier0Result

from backend.models.query_models import VerseItem, QueryRequest, QueryResponse
from backend.config.feature_flags import FEATURE_FLAGS
from backend.core.vocabulary.nql_scripture_vocabulary import resolve_nql_topics
from backend.core.escalation.escalation_messages import get_escalation_message

# Canonical Metadata Isolation (Phase 9.1A.1)
from backend.core.bible_metadata import BIBLE_BOOK_ORDER

# Chapter Metadata Authority (Phase 9.1D)
from backend.core.bible_chapter_metadata import BIBLE_CHAPTER_VERSE_COUNT

# Commentary Layer (Phase 9.1A Option A)
from backend.services.commentary_service import build_commentary
from backend.core.commentary_registry import get_commentator

# Phase 9.1D.2 Reflection Engine
from backend.services.reflection_engine import generate_reflection

# --------------------------------------------------------------
# Phase 9.1D.2.1 — AI Guided Summary Layer
# --------------------------------------------------------------
from backend.services.ai_summary_service import generate_ai_summary
from backend.core.linguistic.linguistic_patterns import (
    combine_verse_text,
    detect_linguistic_patterns,
)

# --------------------------------------------------------------
# Phase 9.1D.2.2 — Pattern Classifier Service
# --------------------------------------------------------------
from backend.services.pattern_classifier_service import classify_pattern

# --------------------------------------------------------------
# Phase 9.1D.2.3 — Theme Interaction Engine
# --------------------------------------------------------------
from backend.services.theme_interaction_engine import interpret_theme_interactions

# --------------------------------------------------------------
# Phase 9.1D.2.3.4 — Expression Builder
# --------------------------------------------------------------
from backend.services.summary_expression_builder import (
    SummaryExpressionBuilder,
    ThemeInteractionResult,
)

# --------------------------------------------------------------
# Phase 9.1F — Reflection (Hands Layer)
# --------------------------------------------------------------
from backend.services.reflection_service import ReflectionService

summary_builder = SummaryExpressionBuilder()

# --------------------------------------------------------------
# Phase 9.1F — Reflection Service Initialization
# --------------------------------------------------------------
reflection_service = ReflectionService()

BIBLE_API_BASE = "https://bible-api.com"

class QueryService:
    # --------------------------------------------------------------
    # Metadata Helpers
    # --------------------------------------------------------------
    def _parse_reference_metadata(self, reference: str):
        for book, (order, testament) in BIBLE_BOOK_ORDER.items():
            if reference.startswith(book):
                return order, testament
        return None, None

    # --------------------------------------------------------------
    # Explicit Scripture Detection
    # --------------------------------------------------------------
    def _is_explicit_verse(self, question: str) -> bool:
        if ":" in question:
            return True
        return False

    # --------------------------------------------------------------
    # Dynamic Scripture Reference Extraction
    # --------------------------------------------------------------
    def _extract_topics(self, question: str) -> List[str]:
        normalized = question.strip()

        pattern = r"(?:[1-3]\s)?[A-Za-z]+\s\d+:\d+(?:-\d+)?"

        matches = re.findall(pattern, normalized)

        if matches:
            return matches

        return [normalized]

    # --------------------------------------------------------------
    # Phase 9.1D — Structural Scope Detection
    # --------------------------------------------------------------
    def _detect_structural_scope(self, verses: List[VerseItem]) -> str:
        if not verses:
            return "unknown"

        if len(verses) == 1:
            return "single_verse"

        chapters = set()
        book_name = None

        for v in verses:
            ref = v.reference or ""

            try:
                left, _ = ref.split(":")
                parts = left.split()

                chapter = int(parts[-1])
                book = " ".join(parts[:-1])

                book_name = book
                chapters.add(chapter)

            except Exception:
                return "verse_range"

        if len(chapters) > 1:
            return "multi_chapter"

        chapter = list(chapters)[0]

        if book_name in BIBLE_CHAPTER_VERSE_COUNT:
            expected = BIBLE_CHAPTER_VERSE_COUNT[book_name].get(chapter)

            if expected and len(verses) == expected:
                return "full_chapter"

        return "verse_range"

    # --------------------------------------------------------------
    # Commentary Formatting
    # --------------------------------------------------------------
    def _commentary_error_to_user_text(self, error_state: Optional[str]) -> str:
        if error_state == "no_excerpts_available":
            return "Historical commentary is not available yet for these verses."
        if error_state == "registry_invalid":
            return "Historical commentary is not available at this time."
        if error_state == "no_valid_verses":
            return "Historical commentary is not available for the current selection."
        if error_state:
            return "Historical commentary is not available at this time."
        return ""

    def _format_commentary_result_as_string(self, commentary_result) -> str:
        if not commentary_result or not getattr(commentary_result, "ordered_blocks", None):
            err = getattr(commentary_result, "error_state", None)
            return self._commentary_error_to_user_text(err)

        lines: List[str] = []

        summary_text = getattr(commentary_result, "summary", None)
        if summary_text:
            lines.append(summary_text.strip())
            lines.append("")

        for block in commentary_result.ordered_blocks:
            label = getattr(block, "label", None) or "Commentary"
            lines.append(f"{label}:")

            items = getattr(block, "items", []) or []

            for it in items:
                ref = getattr(it, "reference", "") or ""
                source_id = getattr(it, "source_id", "") or ""
                excerpt = getattr(it, "excerpt", "") or ""

                source = get_commentator(source_id)
                source_name = source.display_name if source else source_id

                if ref and excerpt and source_name:
                    lines.append(f"- {ref} ({source_name}): {excerpt}")
                elif excerpt:
                    lines.append(f"- {excerpt}")

            lines.append("")

        return "\n".join([ln.rstrip() for ln in lines]).strip()

    # --------------------------------------------------------------
    # Scripture Fetch (Range-Safe)
    # --------------------------------------------------------------
    def fetch_scripture_items(self, reference: str, translation: str = "kjv") -> List[VerseItem]:
        try:
            url = f"{BIBLE_API_BASE}/{requests.utils.quote(reference)}"

            response = requests.get(
                url,
                params={"translation": translation},
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            verse_items: List[VerseItem] = []

            reference_label = (data.get("reference") or reference).strip()

            api_verses = data.get("verses", []) or []

            for v in api_verses:
                verse_text = (v.get("text") or "").strip()

                if not verse_text:
                    continue

                book_name = (v.get("book_name") or "").strip()
                chapter = v.get("chapter")
                verse_number = v.get("verse")

                if book_name and chapter is not None and verse_number is not None:
                    verse_reference = f"{book_name} {chapter}:{verse_number}"
                else:
                    verse_reference = reference_label

                book_order, testament = self._parse_reference_metadata(verse_reference)

                verse_items.append(
                    VerseItem(
                        reference=verse_reference,
                        text=verse_text,
                        book_order=book_order,
                        testament=testament,
                    )
                )

            if verse_items:
                return verse_items

            text = (data.get("text") or "").strip()

            if not text:
                return []

            book_order, testament = self._parse_reference_metadata(reference_label)

            return [
                VerseItem(
                    reference=reference_label,
                    text=text,
                    book_order=book_order,
                    testament=testament,
                )
            ]

        except Exception:
            return []

    # --------------------------------------------------------------
    # Summary Expression Integration Helpers
    # --------------------------------------------------------------
    def _infer_query_type(
        self,
        question: str,
        structural_scope: str,
        explicit_scripture: bool
    ) -> str:
        if not explicit_scripture:
            return "nql"

        if structural_scope == "single_verse":
            return "verse"

        if structural_scope in ("verse_range", "multi_chapter"):
            return "multi_verse"

        if structural_scope == "full_chapter":
            return "chapter"

        return "verse"

    def _safe_string_list(self, value: Any) -> List[str]:
        if value is None:
            return []

        if isinstance(value, list):
            cleaned: List[str] = []
            for item in value:
                if item is None:
                    continue
                text = str(item).strip()
                if text:
                    cleaned.append(text)
            return cleaned

        text = str(value).strip()
        return [text] if text else []

    def _safe_relationships(self, value: Any) -> List[tuple[str, str]]:
        if not isinstance(value, list):
            return []

        relationships: List[tuple[str, str]] = []

        for item in value:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                a = str(item[0]).strip()
                b = str(item[1]).strip()
                if a and b:
                    relationships.append((a, b))

        return relationships

    def _translate_pattern_to_motif(self, pattern: str) -> Optional[str]:
        normalized = (pattern or "").strip().lower()

        if not normalized:
            return None

        supported_motifs = {
            "love",
            "sacrifice",
            "redemption",
            "life",
            "fear",
            "faith",
            "justice",
            "mercy",
            "creation",
            "promise",
            "teaching",
            "wisdom",
            "instruction",
            "warning",
        }

        if normalized in supported_motifs:
            return normalized

        translation_map = {
            "command": "instruction",
            "commands": "instruction",
            "instructional": "instruction",
            "teaches": "teaching",
            "teaching": "teaching",
            "promise": "promise",
            "promises": "promise",
            "warning": "warning",
            "warnings": "warning",
            "wisdom": "wisdom",
            "poetry": "wisdom",
            "poetic": "wisdom",
            "parable": "teaching",
            "parables": "teaching",
            "judgment": "justice",
            "compassion": "mercy",
            "restoration": "redemption",
            "salvation": "redemption",
            "created": "creation",
            "creates": "creation",
            "narrative": "life",
        }

        return translation_map.get(normalized)

    def _translate_patterns_to_motifs(
        self,
        dominant_pattern: Any,
        candidate_patterns: List[str]
    ) -> List[str]:
        motifs: List[str] = []
        seen = set()

        ordered_patterns: List[str] = []

        dominant_text = str(dominant_pattern or "").strip()
        if dominant_text:
            ordered_patterns.append(dominant_text)

        ordered_patterns.extend(candidate_patterns or [])

        for pattern in ordered_patterns:
            motif = self._translate_pattern_to_motif(pattern)
            if not motif or motif in seen:
                continue

            motifs.append(motif)
            seen.add(motif)

        return motifs

    def _extract_detected_motifs(
        self,
        semantic_motifs: List[str],
        theme_analysis: Any
    ) -> List[str]:
        if hasattr(theme_analysis, "detected_motifs"):
            motifs = self._safe_string_list(getattr(theme_analysis, "detected_motifs"))
            if motifs:
                return motifs

        if isinstance(theme_analysis, dict) and "detected_motifs" in theme_analysis:
            motifs = self._safe_string_list(theme_analysis.get("detected_motifs"))
            if motifs:
                return motifs

        return self._safe_string_list(semantic_motifs)

    def _extract_motif_relationships(self, theme_analysis: Any) -> List[tuple[str, str]]:
        if hasattr(theme_analysis, "motif_relationships"):
            return self._safe_relationships(getattr(theme_analysis, "motif_relationships"))

        if isinstance(theme_analysis, dict) and "motif_relationships" in theme_analysis:
            return self._safe_relationships(theme_analysis.get("motif_relationships"))

        return []


    def _extract_supporting_movements(
        self,
        ai_summary: str,
        theme_analysis: Any,
        detected_motifs: List[str]
    ) -> List[str]:
        if hasattr(theme_analysis, "supporting_movements"):
            movements = self._safe_string_list(getattr(theme_analysis, "supporting_movements"))
            if movements:
                return movements

        if isinstance(theme_analysis, dict) and "supporting_movements" in theme_analysis:
            movements = self._safe_string_list(theme_analysis.get("supporting_movements"))
            if movements:
                return movements

        # Phase 9.1D.2.8 — removed hardcoded fallback
        return []

    def _extract_central_conclusion(
        self,
        ai_summary: str,
        fallback_summary: str,
        theme_analysis: Any,
        detected_motifs: List[str]
    ) -> str:
        if hasattr(theme_analysis, "central_conclusion"):
            conclusion = str(getattr(theme_analysis, "central_conclusion") or "").strip()
            if conclusion:
                return conclusion

        if isinstance(theme_analysis, dict):
            conclusion = str(theme_analysis.get("central_conclusion") or "").strip()
            if conclusion:
                return conclusion

        # Phase 9.1D.2.8 — removed hardcoded fallback
        return ""

    def _build_theme_interaction_result(
        self,
        req: QueryRequest,
        question: str,
        structural_scope: str,
        verse_items: List[VerseItem],
        semantic_motifs: List[str],
        theme_analysis: Any,
        ai_summary: str,
        fallback_summary: str,
        explicit_scripture: bool,
    ) -> ThemeInteractionResult:
        combined_text = combine_verse_text(verse_items)

        query_type = self._infer_query_type(
            question=question,
            structural_scope=structural_scope,
            explicit_scripture=explicit_scripture,
        )

        translation = (req.translation or "kjv").upper()

        passage_reference = verse_items[0].reference if verse_items else question

        if len(verse_items) > 1:
            passage_reference = verse_items[0].reference

        detected_motifs = self._extract_detected_motifs(semantic_motifs, theme_analysis)
        motif_relationships = self._extract_motif_relationships(theme_analysis)
        supporting_movements = self._extract_supporting_movements(
            ai_summary,
            theme_analysis,
            detected_motifs,
        )

        # Phase 9.1D.2.8 — Meaning Engine Integration (CONDUCTOR ONLY)

        from backend.services.meaning_engine import build_meaning

        meaning = build_meaning(
            passage_text=combined_text,
            motifs=detected_motifs,
            relationships=motif_relationships,
            user_question=question
    )

        central_conclusion = meaning.get("core", "")
        supporting_movements = meaning.get("expansion", [])

        return ThemeInteractionResult(
            query_type=query_type,
            translation=translation,
            passage_reference=passage_reference,
            passage_text=combined_text,
            detected_motifs=detected_motifs,
            motif_relationships=motif_relationships,
            central_conclusion=central_conclusion,
            supporting_movements=supporting_movements,
        )

    def _summary_violates_guardrails(self, summary: str, passage_text: str) -> bool:
        if not summary or len(summary.strip()) < 25:
            return True

        lowered = summary.lower().strip()

        forbidden_terms = [
            "theme",
            "themes",
            "motif",
            "motifs",
            "interaction",
            "interactions",
            "linguistic",
            "pattern",
            "patterns",
            "detected",
            "analysis",
            "algorithm",
            "connects ",
        ]

        if any(term in lowered for term in forbidden_terms):
            return True

        passage_lower = (passage_text or "").lower().strip()

        if passage_lower and lowered == passage_lower:
            return True

        return False

    # --------------------------------------------------------------
    # Main Execution
    # --------------------------------------------------------------
    def process_query(self, req: Union[QueryRequest, dict]) -> QueryResponse:
        if isinstance(req, dict):
            req = QueryRequest(**req)

        print("🔥 NEW QUERY SERVICE VERSION ACTIVE 🔥")

        want_commentary: bool = bool(getattr(req, "want_commentary", False))

        question = (req.question or "").strip()

        if len(question) < 3:
            raise HTTPException(
                status_code=400,
                detail="I want to walk with you in this reflection. Could you share a little more about what you’re seeking?"
            )

        normalized_question = question.lower().strip()

        tier0_result: Tier0Result = detect_tier0(normalized_question)

        escalation_level = route_escalation_level(
            crisis_type=tier0_result.crisis_type,
            confidence=tier0_result.confidence,
            route_map=FEATURE_FLAGS.get("CRISIS_ROUTE_MAP", {}),
            high_conf_threshold=FEATURE_FLAGS.get("CRISIS_HIGH_CONF_THRESHOLD", 0.33),
        )

        if escalation_level in ("hard_stop", "redirect_support"):
            escalation_payload = get_escalation_message(escalation_level)

            return QueryResponse(
                verses=[],
                summary=escalation_payload.get("message", ""),
                commentary=None,
                context=None,
                reflection=None,
                want_commentary=None,
                escalation_level=escalation_level,
            )

        verse_items: List[VerseItem] = []
        explicit_scripture = self._is_explicit_verse(question)

        if explicit_scripture:
            topics = self._extract_topics(question)

            for topic in topics:
                fetched = self.fetch_scripture_items(topic, req.translation or "kjv")
                if fetched:
                    verse_items.extend(fetched)
        
        else:
            query_for_resolution = question

            print("DEBUG QUERY:", query_for_resolution)

            from backend.core.vocabulary.nql_scripture_vocabulary import resolve_scripture_with_llm

            # Phase 10B — LLM direct scripture resolution
            refs = resolve_scripture_with_llm(query_for_resolution)

            # Fallback to existing system
            if not refs:
                refs = resolve_nql_topics(query_for_resolution)   

            for ref in refs:
                fetched = self.fetch_scripture_items(ref, req.translation or "kjv")
                if fetched:
                    verse_items.extend(fetched)

        if not verse_items:
            raise HTTPException(
                status_code=422,
                detail="I want to make sure I reflect what you’re really seeking. Could you share a little more about what’s behind this question?"
            )

        verse_items.sort(
            key=lambda v: (v.testament != "OT", v.book_order or 999)
        )

        structural_scope = self._detect_structural_scope(verse_items)

        commentary_text: Optional[str] = None

        if want_commentary and verse_items:
            c_res = build_commentary(verses=verse_items)
            formatted = self._format_commentary_result_as_string(c_res)
            commentary_text = formatted or None

        # ----------------------------------------------------------
        # Phase 9.1D.2.1 — AI Guided Summary Attempt
        # ----------------------------------------------------------
        combined_text = combine_verse_text(verse_items)

        pattern_scores = detect_linguistic_patterns(combined_text)

        signals = []
        if pattern_scores:
            signals = [p[0] for p in pattern_scores[:2]]

        # ----------------------------------------------------------
        # Phase 9.1D.2.2 — Pattern Classification Layer
        # ----------------------------------------------------------
        candidate_patterns = []

        if pattern_scores:
            candidate_patterns = [p[0] for p in pattern_scores[:3]]

        dominant_pattern = classify_pattern(
            combined_text,
            candidate_patterns,
            llm_client=None
        )

        # ----------------------------------------------------------
        # Phase 9.1D.2.2.5 — Pattern → Motif Translation Layer
        # ----------------------------------------------------------
        semantic_motifs = self._translate_patterns_to_motifs(
            dominant_pattern=dominant_pattern,
            candidate_patterns=candidate_patterns,
        )

        # ----------------------------------------------------------
        # Phase 9.1D.2.3 — Theme Interaction Engine
        # ----------------------------------------------------------
        theme_analysis = interpret_theme_interactions(semantic_motifs)

        ai_summary = generate_ai_summary(
            verses=verse_items,
            structural_scope=structural_scope,
            signals=signals,
            llm_client=None
        )

        # ----------------------------------------------------------
        # Phase 9.1D.2.3.4 — Summary Expression Builder Integration
        # ----------------------------------------------------------

        try:
            print("QUERY SERVICE: BUILDING SUMMARY")

            theme_result = self._build_theme_interaction_result(
                req=req,
                question=question,
                structural_scope=structural_scope,
                verse_items=verse_items,
                semantic_motifs=semantic_motifs,
                theme_analysis=theme_analysis,
                ai_summary=ai_summary or "",
                fallback_summary="",
                explicit_scripture=explicit_scripture,
            )

            # ----------------------------------------------------------
            # SUMMARY MODEL V1 — BUILD FINAL SUMMARY STRING
            # ----------------------------------------------------------

            print("DEBUG THEME RESULT:")
            print("  meaning =", theme_result)

            core = getattr(theme_result, "central_conclusion", "") or ""
            expansion = getattr(theme_result, "supporting_movements", []) or []
            resolution = ""  # Not used yet

            summary_parts = []

            if core:
                summary_parts.append(core)

            if expansion:
                summary_parts.extend(expansion)

            if resolution:
                summary_parts.append(resolution)

            final_summary = "\n\n".join(summary_parts).strip()

            print("QUERY SERVICE: FINAL SUMMARY (V1) =", final_summary)

        except Exception as e:
            print("QUERY SERVICE: SUMMARY BUILD FAILED =", str(e))
            final_summary = ""

        # --------------------------------------------------------------
        # Phase 9.1F — Reflection Build (Hands Layer)
        # --------------------------------------------------------------
        reflection = ""
        if 'theme_result' in locals() and theme_result:

            from backend.services.ai_reflection_service import generate_ai_reflection
            reflection = generate_ai_reflection(theme_result)

        return QueryResponse(
            verses=verse_items,
            summary=final_summary,
            reflection=reflection,
            commentary=commentary_text,
            want_commentary=want_commentary,
            escalation_level=escalation_level,
        ) 
