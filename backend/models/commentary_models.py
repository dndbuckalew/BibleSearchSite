"""
Commentary Layer Data Models
Phase 9.1 — Implementation (Models Only)

Governance Notes:
- Pure data structures only
- No business logic
- No registry access
- No service imports
- No escalation logic
- No reflection blending
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Literal


# -----------------------------
# Source Metadata Model
# -----------------------------

TestamentType = Literal["OT", "NT", "BOTH"]

EmphasisType = Literal[
    "devotional",
    "expository",
    "linguistic",
    "historical",
    "practical",
]


@dataclass(frozen=True)
class CommentatorSource:
    source_id: str
    display_name: str
    public_domain_verified: bool
    attribution: str
    testament_applicability: TestamentType
    emphasis: List[EmphasisType]
    approved: bool = True
    url: Optional[str] = None
    notes: Optional[str] = None


# -----------------------------
# Verse-Bound Commentary Excerpt
# -----------------------------

@dataclass
class VerseCommentaryExcerpt:
    reference: str
    testament: Literal["OT", "NT"]
    source_id: str
    excerpt: str
    confidence: Optional[float] = None
    warnings: List[str] = field(default_factory=list)


# -----------------------------
# Testament Block (Display Unit)
# -----------------------------

@dataclass
class TestamentBlock:
    testament: Literal["NT", "OT"]
    label: str
    items: List[VerseCommentaryExcerpt]


# -----------------------------
# Aggregated Commentary Result
# -----------------------------

@dataclass
class CommentaryResult:
    ordered_blocks: List[TestamentBlock]
    summary: Optional[str] = None
    suppressed: bool = False
    error_state: Optional[str] = None
    