"""
BTA V4
Context Theme Registry

Temporary authority for Context participation themes.

Future authority:
PostgreSQL Context Theme Registry

Themes are governed definitions and must not be
hardcoded inside runtime context logic.
"""

CONTEXT_THEME_REGISTRY = [
    {
        "theme_id": "scene",
        "theme_name": "Scene Context",
        "enabled": True,
    },
    {
        "theme_id": "relationship",
        "theme_name": "Relationship Context",
        "enabled": True,
    },
    {
        "theme_id": "historical",
        "theme_name": "Historical Context",
        "enabled": True,
    },
    {
        "theme_id": "composition",
        "theme_name": "Composition Context",
        "enabled": True,
    },
    {
        "theme_id": "covenant",
        "theme_name": "Covenant Context",
        "enabled": True,
    },
    {
        "theme_id": "participation",
        "theme_name": "Participation Context",
        "enabled": True,
    },
    {
        "theme_id": "passage_scope",
        "theme_name": "Passage Scope Context",
        "enabled": True,
    },
]
