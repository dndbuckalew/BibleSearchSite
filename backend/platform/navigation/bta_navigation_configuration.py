"""
===============================================================================
Platform Capability: Navigation
Domain Configuration: Bible Therapy Assistant™ (BTA)

File:
    bta_navigation_configuration.py

Purpose:
    Defines the navigation configuration for the Bible Therapy Assistant™
    domain.

Responsibilities:
    - Define the BTA navigation structure.
    - Supply the Platform Navigation capability with domain-specific
      navigation configuration.
    - Maintain a single authoritative source for BTA navigation.

Non-Responsibilities:
    - No rendering logic.
    - No frontend UI logic.
    - No routing implementation.
    - No workspace implementation.

Future:
    Additional domain navigation configuration files (OSHA, VA, NEC, etc.)
    shall follow this same structure.

Architecture:
    BibleSearchSite (Current)
        backend/platform/navigation/

    Future
        HCGO Orchestration Layer
            platform/navigation/

===============================================================================
"""

# =============================================================================
# BTA Navigation Configuration
# =============================================================================

BTA_NAVIGATION_CONFIGURATION = {

    "header": {
        "brand": {
            "label": "Bible Therapy Assistant™",
            "home_path": "/",
            "logo_path": None,
        },
        "items": [
            {
                "id": "home",
                "label": "Home",
                "action": "navigate",
                "target": "/",
            },
            {
                "id": "stay-connected",
                "label": "Stay Connected",
                "action": "open_workspace",
                "target": "stay-connected",
            },
            {
                "id": "donate",
                "label": "Donate",
                "action": "open_workspace",
                "target": "donation",
            },
            {
                "id": "menu",
                "label": "Menu",
                "action": "open_menu",
                "target": "main-menu",
            },
        ],
    },

    "menu": {
        "items": [
            {
                "id": "about-bta",
                "label": "About BTA",
                "children": [
                    "Mission",
                    "How BTA Works",
                    "What Makes BTA Different",
                    "What's New",
                    "Release Notes",
                    "Version Information",
                    "Patent Pending",
                    "Contact",
                ],
            },
        ],
    },

}

