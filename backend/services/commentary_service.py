"""
Commentary Service Layer
Phase 9.1 — Implementation (Service Only)

Governance Notes:
- Verse-bound only (operates ONLY on resolved verses passed in)
- No emotional state inputs
- No escalation inputs (Option 1: escalation gating is owned by query_service)
- No reflection blending
- Registry-approved sources only
- Neutral, bounded behavior
- No raw exception leakage (errors are logged internally; safe error_state codes returned)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from backend.core.commentary_registry import (
    get_commentator,
    list_commentators,
    validate_registry,
)
from backend.core.commentary_data.canonical_commentary_dataset import (
    CANONICAL_COMMENTARY_DATASET,
)
from backend.models.commentary_models import (
    CommentaryResult,
    TestamentBlock,
    VerseCommentaryExcerpt,
)

logger = logging.getLogger(__name__)


# -----------------------------
# Bounded Controls (Locked)
# -----------------------------

DEFAULT_EXCERPT_MAX_CHARS = 650
DEFAULT_SUMMARY_MAX_CHARS = 500
SUMMARY_LEAD_IN = (
    "Summary of recurring themes across selected historical commentators."
)


# -----------------------------
# Public API
# -----------------------------


def build_commentary(
    *,
    verses: Sequence[Any],
    testament_override: Optional[str] = None,
    selected_sources: Optional[Sequence[str]] = None,
    excerpt_max_chars: int = DEFAULT_EXCERPT_MAX_CHARS,
    summary_max_chars: int = DEFAULT_SUMMARY_MAX_CHARS,
) -> CommentaryResult:

    if not verses:
        return CommentaryResult(
            ordered_blocks=[], summary=None, suppressed=False, error_state=None
        )

    try:
        validate_registry()
    except Exception:
        logger.exception("Commentary registry validation failed.")
        return CommentaryResult(
            ordered_blocks=[],
            summary=None,
            suppressed=False,
            error_state="registry_invalid",
        )

    order = _resolve_testament_order(testament_override)
    approved_source_ids = _resolve_sources(selected_sources)

    verse_primitives: List[Tuple[str, str]] = []
    for v in verses:
        ref = _extract_reference(v)
        tst = _extract_testament(v)
        if not ref or tst not in ("NT", "OT"):
            continue
        verse_primitives.append((ref, tst))

    if not verse_primitives:
        return CommentaryResult(
            ordered_blocks=[],
            summary=None,
            suppressed=False,
            error_state="no_valid_verses",
        )

    excerpts: List[VerseCommentaryExcerpt] = []

    for reference, testament in verse_primitives:
        for source_id in approved_source_ids:
            if not get_commentator(source_id):
                continue

            excerpt_text = _retrieve_excerpt(
                source_id=source_id,
                reference=reference,
            )

            if not excerpt_text:
                continue

            excerpt_text = _enforce_excerpt_bounds(
                excerpt_text,
                excerpt_max_chars,
            )

            excerpts.append(
                VerseCommentaryExcerpt(
                    reference=reference,
                    testament=testament,
                    source_id=source_id,
                    excerpt=excerpt_text,
                    confidence=None,
                    warnings=[],
                )
            )

    blocks = _build_testament_blocks(excerpts=excerpts, order=order)

    summary = None
    if excerpts:
        summary = _generate_neutral_summary(
            excerpts=excerpts,
            max_chars=summary_max_chars,
        )

    if not excerpts:
        return CommentaryResult(
            ordered_blocks=[],
            summary=None,
            suppressed=False,
            error_state="no_excerpts_available",
        )

    return CommentaryResult(
        ordered_blocks=blocks,
        summary=summary,
        suppressed=False,
        error_state=None,
    )


# -----------------------------
# Internal Helpers
# -----------------------------


def _resolve_testament_order(testament_override: Optional[str]) -> List[str]:
    """
    Default ordering follows canonical Bible structure:
    OT (Genesis → Malachi)
    NT (Matthew → Revelation)
    """
    override = (testament_override or "").strip().upper()

    if override == "NT_FIRST":
        return ["NT", "OT"]

    return ["OT", "NT"]


def _resolve_sources(selected_sources: Optional[Sequence[str]]) -> List[str]:
    if selected_sources:
        out: List[str] = []
        for sid in selected_sources:
            sid_norm = (sid or "").strip()
            if sid_norm and get_commentator(sid_norm):
                out.append(sid_norm)
        return out

    return [s.source_id for s in list_commentators()]


def _extract_reference(verse: Any) -> Optional[str]:
    if verse is None:
        return None
    try:
        if isinstance(verse, dict):
            return _clean_str(verse.get("reference") or verse.get("ref"))
        return _clean_str(
            getattr(verse, "reference", None)
            or getattr(verse, "ref", None)
        )
    except Exception:
        return None


def _extract_testament(verse: Any) -> Optional[str]:
    if verse is None:
        return None
    try:
        raw = verse.get("testament") if isinstance(verse, dict) else getattr(verse, "testament", None)
        raw_norm = _clean_str(raw)
        if not raw_norm:
            return None

        upper = raw_norm.upper()
        if upper in ("NT", "NEW", "NEW_TESTAMENT"):
            return "NT"
        if upper in ("OT", "OLD", "OLD_TESTAMENT"):
            return "OT"
        return None
    except Exception:
        return None


# 🔥 FIXED FUNCTION — SAFE NORMALIZED MATCHING
def _retrieve_excerpt(*, source_id: str, reference: str) -> Optional[str]:
    """
    Controlled dataset retrieval (Phase 9.1C).

    Deterministic.
    Case-insensitive.
    Whitespace-normalized.
    No fuzzy logic.
    """

    verse_ref = (reference or "").strip().lower()

    for record in CANONICAL_COMMENTARY_DATASET:
        rec_ref = (record.get("reference") or "").strip().lower()

        if (
            record.get("source_id") == source_id
            and rec_ref == verse_ref
        ):
            return record.get("excerpt")

    return None


def _enforce_excerpt_bounds(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text

    trimmed = text[:max_chars].rstrip()
    trimmed = re.sub(r"\s+\S*$", "", trimmed).rstrip()
    return (trimmed + "…") if trimmed else (text[:max_chars].rstrip() + "…")


def _build_testament_blocks(
    *,
    excerpts: List[VerseCommentaryExcerpt],
    order: List[str],
) -> List[TestamentBlock]:

    by_testament: Dict[str, List[VerseCommentaryExcerpt]] = {
        "NT": [],
        "OT": [],
    }

    for ex in excerpts:
        if ex.testament in by_testament:
            by_testament[ex.testament].append(ex)

    blocks: List[TestamentBlock] = []

    for t in order:
        items = by_testament.get(t, [])
        if not items:
            continue

        label = (
            "New Testament Commentary"
            if t == "NT"
            else "Old Testament Commentary"
        )

        blocks.append(
            TestamentBlock(
                testament=t,
                label=label,
                items=items,
            )
        )

    return blocks


def _generate_neutral_summary(
    *,
    excerpts: List[VerseCommentaryExcerpt],
    max_chars: int,
) -> str:

    per_source_tokens: Dict[str, set] = {}

    for ex in excerpts:
        tokens = _tokenize(ex.excerpt)
        per_source_tokens.setdefault(ex.source_id, set()).update(tokens)

    if len(per_source_tokens) < 1:
        return _bound_text(SUMMARY_LEAD_IN, max_chars)

    all_terms: Dict[str, int] = {}
    for toks in per_source_tokens.values():
        for term in toks:
            all_terms[term] = all_terms.get(term, 0) + 1

    threshold = 2 if len(per_source_tokens) >= 2 else 1
    recurring = [t for t, c in all_terms.items() if c >= threshold]

    recurring = sorted(recurring)[:8]

    if recurring:
        body = (
            f"{SUMMARY_LEAD_IN} Common recurring terms include: "
            + ", ".join(recurring)
            + "."
        )
    else:
        body = SUMMARY_LEAD_IN

    return _bound_text(body, max_chars)


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    raw = [t for t in text.split() if 3 <= len(t) <= 18]

    stop = {
        "the", "and", "for", "that", "with", "this", "from", "into",
        "they", "their", "them", "you", "your", "his", "her",
        "she", "him", "was", "were", "are", "but", "not",
        "have", "has", "had", "will", "shall", "may", "might",
        "can", "could", "would", "should", "also", "than",
        "then", "when", "what", "which", "who", "whom",
        "why", "how",
    }

    return [t for t in raw if t not in stop]


def _bound_text(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""

    text = (text or "").strip()
    if len(text) <= max_chars:
        return text

    return text[: max_chars - 1].rstrip() + "…"


def _clean_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    try:
        s = str(val).strip()
        return s if s else None
    except Exception:
        return None
              