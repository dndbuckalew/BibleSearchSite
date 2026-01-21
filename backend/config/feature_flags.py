# config/feature_flags.py
# PURPOSE: Centralized runtime execution controls for BTA

FEATURE_FLAGS = {
    "ENABLE_PERSONAS": True,
    "ENABLE_FLIPPED_INTERACTION": False,
    "ENABLE_EMOTIONAL_SIGNALING": False,
    "ENABLE_LLM_RESPONSES": False,
    "ENABLE_SAFETY_ESCALATION": False,

    # Emergency controls
    "FORCE_SAFE_MODE": False,      # disables personas + LLMs
    "LOG_VERBOSE": True
}
