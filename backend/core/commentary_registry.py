"""
Commentary Source Registry
Phase 9.1 — Registry Authority Layer

Governance Notes:
- Metadata authority only
- No excerpt storage
- No verse selection logic
- No escalation interaction
- No summary generation
- No user input logic
"""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.models.commentary_models import CommentatorSource


# -------------------------------------------------------
# Approved Commentary Source Registry (Authority Layer)
# -------------------------------------------------------

APPROVED_COMMENTATORS: Dict[str, CommentatorSource] = {
    "matthew_henry": CommentatorSource(
        source_id="matthew_henry",
        display_name="Matthew Henry",
        public_domain_verified=True,
        attribution="Matthew Henry Commentary (Public Domain)",
        testament_applicability="BOTH",
        emphasis=["devotional", "expository"],
        approved=True,
        url=None,
        notes="Classic devotional-expository commentary.",
    ),
    "jamieson_fausset_brown": CommentatorSource(
        source_id="jamieson_fausset_brown",
        display_name="Jamieson-Fausset-Brown",
        public_domain_verified=True,
        attribution="Jamieson-Fausset-Brown Commentary (Public Domain)",
        testament_applicability="BOTH",
        emphasis=["expository", "historical", "linguistic"],
        approved=True,
        url=None,
        notes="Historical and linguistic emphasis.",
    ),
    "john_wesley": CommentatorSource(
    source_id="john_wesley",
    display_name="John Wesley",
    public_domain_verified=True,
    attribution="John Wesley Commentary (Public Domain)",
    testament_applicability="BOTH",
    emphasis=["practical", "devotional"],
    approved=True,
    url=None,
    notes="Methodist theologian.",
),

"charles_spurgeon": CommentatorSource(
    source_id="charles_spurgeon",
    display_name="Charles Spurgeon",
    public_domain_verified=True,
    attribution="Charles Spurgeon Commentary (Public Domain)",
    testament_applicability="BOTH",
    emphasis=["devotional", "practical"],
    approved=True,
    url=None,
    notes="Baptist preacher.",
),

"adam_clarke": CommentatorSource(
    source_id="adam_clarke",
    display_name="Adam Clarke",
    public_domain_verified=True,
    attribution="Adam Clarke Commentary (Public Domain)",
    testament_applicability="BOTH",
    emphasis=["expository", "linguistic"],
    approved=True,
    url=None,
    notes="Biblical scholar.",
),

"albert_barnes": CommentatorSource(
    source_id="albert_barnes",
    display_name="Albert Barnes",
    public_domain_verified=True,
    attribution="Albert Barnes Commentary (Public Domain)",
    testament_applicability="BOTH",
    emphasis=["expository", "practical"],
    approved=True,
    url=None,
    notes="Biblical commentator.",
),
}


# -------------------------------------------------------
# Registry Utilities
# -------------------------------------------------------

def get_commentator(source_id: str) -> Optional[CommentatorSource]:
    """
    Retrieve a commentator by source_id.
    Returns None if not found or not approved.
    """
    source = APPROVED_COMMENTATORS.get(source_id)
    if source and source.approved and source.public_domain_verified:
        return source
    return None


def list_commentators() -> List[CommentatorSource]:
    """
    Return list of approved, public-domain commentators.
    """
    return [
        source
        for source in APPROVED_COMMENTATORS.values()
        if source.approved and source.public_domain_verified
    ]


def validate_registry() -> None:
    """
    Governance validation to ensure registry integrity.

    Raises:
        ValueError if structural issues are detected.
    """
    seen_ids = set()

    for source_id, source in APPROVED_COMMENTATORS.items():
        if source_id in seen_ids:
            raise ValueError(f"Duplicate source_id detected: {source_id}")
        seen_ids.add(source_id)

        if not source.public_domain_verified:
            raise ValueError(f"Source not verified public domain: {source_id}")

        if not source.attribution:
            raise ValueError(f"Missing attribution for source: {source_id}")

        if not source.testament_applicability:
            raise ValueError(f"Missing testament applicability: {source_id}")

        if not source.approved:
            raise ValueError(f"Unapproved source present in registry: {source_id}")
