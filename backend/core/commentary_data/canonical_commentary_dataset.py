"""
Canonical Commentary Dataset
Phase 9.1C — Controlled Dataset Enablement

Governance Rules:
- Public-domain sources only
- Registry-authoritative metadata (no duplication here)
- No display_name
- No emphasis
- No attribution
- No URLs
- No logic
- No synthesis
- Verse-bound excerpts only
"""

from typing import Dict, List


# Each record must contain:
# - reference (str)
# - testament ("OT" or "NT")
# - source_id (must match registry)
# - excerpt (bounded later by service layer)


CANONICAL_COMMENTARY_DATASET: List[Dict[str, str]] = [

    # --- NEW TESTAMENT ---
    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "matthew_henry",
        "perspective": "Classical devotional-expository commentary.",

        # --------------------------------------------------
        # PILOT TEST DATA
        #
        # Source:
        # Google search result summarizing Matthew Henry
        #
        # Purpose:
        # Commentary plumbing validation
        #
        # NOT production commentary content.
        # Replace during commentary population phase.
        # --------------------------------------------------

        "excerpt": (
            "God loved the world and gave His only begotten Son "
            "for its salvation. This demonstrates the freeness "
            "of divine grace and the greatness of God's love "
            "toward undeserving sinners."
        )
    },
    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "john_wesley",

        # --------------------------------------------------
        # PILOT TEST DATA
        #
        # Source:
        # Google search result summarizing John Wesley
        #
        # Purpose:
        # Multi-scholar architecture validation
        #
        # NOT production commentary content.
        # Replace during commentary population phase.
        # --------------------------------------------------

        "excerpt": (
            "God's love is freely offered to all mankind through "
            "His Son. Whoever believes in Christ receives eternal "
            "life, demonstrating both the universality of God's "
            "grace and the promise of salvation."
        )
    },
    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "charles_spurgeon",

        # --------------------------------------------------
        # PILOT TEST DATA
        #
        # Source:
        # Google search result summarizing Charles Spurgeon
        #
        # Purpose:
        # Multi-scholar architecture validation
        #
        # NOT production commentary content.
        # Replace during commentary population phase.
        # --------------------------------------------------

        "excerpt": (
            "The gift of God's Son reveals the immeasurable depth "
            "of divine love. Through Christ, sinners are offered "
            "forgiveness, eternal life, and reconciliation with God."
        )
    },
    {
        "reference": "Romans 5:1",
        "testament": "NT",
        "source_id": "jamieson_fausset_brown",
        "excerpt": "PLACEHOLDER_EXCERPT_NT_2"
    },
    {
        "reference": "Ephesians 2:8",
        "testament": "NT",
        "source_id": "matthew_henry",
        "excerpt": "PLACEHOLDER_EXCERPT_NT_3"
    },

    # --- OLD TESTAMENT ---
    {
        "reference": "Genesis 1:1",
        "testament": "OT",
        "source_id": "matthew_henry",
        "excerpt": "PLACEHOLDER_EXCERPT_OT_1"
    },
    {
        "reference": "Psalm 23:1",
        "testament": "OT",
        "source_id": "jamieson_fausset_brown",
        "excerpt": "PLACEHOLDER_EXCERPT_OT_2"
    },
    {
        "reference": "Isaiah 53:5",
        "testament": "OT",
        "source_id": "matthew_henry",
        "excerpt": "PLACEHOLDER_EXCERPT_OT_3"
    },
]
