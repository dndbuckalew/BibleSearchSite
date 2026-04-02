"""
PURPOSE:
Centralized runtime execution controls for the Bible Therapy Assistant (BTA).

Design principles:
- Feature flags are authoritative and explicit
- Development-only scaffolding must never leak to production
- Production behavior is SAFE by default
- Environment must be explicitly set to enable dev-only behavior
"""

import os

# --------------------------------------------------------------
# Environment
# --------------------------------------------------------------
# SAFE DEFAULT:
# If ENV is not set, system assumes "production"
# Development behavior must be explicitly enabled via ENV=development
# --------------------------------------------------------------

ENV = os.getenv("ENV", "production").strip().lower()

# Only explicit "development" enables dev features
IS_DEV = ENV == "development"

# Optional visibility for startup logs (safe to keep)
print(f"[BTA] Environment: {ENV}")
print(f"[BTA] Development mode: {IS_DEV}")

# --------------------------------------------------------------
# Feature Flags
# --------------------------------------------------------------

FEATURE_FLAGS = {

    # ----------------------------------------------------------
    # Core capability toggles
    # ----------------------------------------------------------
    "ENABLE_PERSONAS": True,
    "ENABLE_FLIPPED_INTERACTION": False,
    "ENABLE_EMOTIONAL_SIGNALING": False,
    "ENABLE_LLM_RESPONSES": False,

    # Safety escalation must be explicitly enabled
    "ENABLE_SAFETY_ESCALATION": True,

    # ----------------------------------------------------------
    # Emergency / safety controls
    # ----------------------------------------------------------
    "FORCE_SAFE_MODE": False,      # disables personas + LLMs immediately
    "LOG_VERBOSE": IS_DEV,         # verbose logging only in development

    # ----------------------------------------------------------
    # Phase 9.6 — Dev-only deterministic plumbing
    # ----------------------------------------------------------
    # Used ONLY to validate HEART → HANDS wiring
    # Automatically disabled outside development
    # ----------------------------------------------------------
    "FORCE_DETERMINISTIC_RESULTS": IS_DEV,

    # ----------------------------------------------------------
    # Phase 9.8A / 9.8B — Escalation Routing Controls
    # ----------------------------------------------------------

    # Explicit crisis routing map
    "CRISIS_ROUTE_MAP": {
        "SUICIDAL_INTENT": "hard_stop",
        "SELF_HARM": "hard_stop",
        "HARM_TO_OTHERS": "redirect_support",
        "ABUSE_OR_DANGER": "support_overlay",
    },

    # Revised deterministic threshold per 9.8B.5 Amendment
    # 1 hit (confidence 0.33) now escalates
    "CRISIS_HIGH_CONF_THRESHOLD": 0.33,
}
