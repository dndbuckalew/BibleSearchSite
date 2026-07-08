"""
BTA Commentary Repository

Operational Commentary Data Model

Purpose:
Provides BTA-owned commentary records for the Commentary domain.

Governance:
- BTA-owned artifact
- Public-domain commentary sources only
- Verse-bound excerpts only
- No synthesis
- No interpretation by repository
- Registry remains authoritative for scholar metadata
"""

from typing import Dict, List

BTA_COMMENTARY_REPOSITORY: List[Dict[str, str]] = [

    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "matthew_henry",
        "perspective": "Classical devotional-expository commentary.",
        "excerpt": (
            "God loved the world and gave His only begotten Son "
            "for its salvation. This demonstrates the freeness "
            "of divine grace and the greatness of God's love "
            "toward undeserving sinners."
        ),
    },

    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "john_wesley",
        "excerpt": (
            "God's love is freely offered to all mankind through "
            "His Son. Whoever believes in Christ receives eternal "
            "life, demonstrating both the universality of God's "
            "grace and the promise of salvation."
        ),
    },

    {
        "reference": "John 3:16",
        "testament": "NT",
        "source_id": "charles_spurgeon",
        "excerpt": (
            "The gift of God's Son reveals the immeasurable depth "
            "of divine love. Through Christ, sinners are offered "
            "forgiveness, eternal life, and reconciliation with God."
        ),
    },

]

def get_commentary_records(reference: str) -> List[Dict[str, str]]:
    """
    Retrieve all commentary records for a Scripture reference.
    """

    verse_ref = (reference or "").strip().lower()

    matching_records: List[Dict[str, str]] = []

    for record in BTA_COMMENTARY_REPOSITORY:
        rec_ref = (record.get("reference") or "").strip().lower()

        if rec_ref == verse_ref:
            matching_records.append(record)

    return matching_records

    