# backend/config/crisis_vocabulary.py
"""
BTA Phase 9.8A.2 — Crisis Vocabulary Canonicalization
Governance Authority File

This file defines the canonical Tier 0 deterministic crisis vocabulary.
This file does NOT contain enforcement logic.
This file does NOT perform routing.
This file does NOT interpret context.

Mechanical Constraints:
- Deterministic substring matching only
- No stemming
- No lemmatization
- No fuzzy matching
- No inference
- No LLM involvement

Vocabulary expansion requires a new constitutional phase.
"""

KEYWORDS_BY_CRISIS_TYPE = {

    "SUICIDAL_INTENT": [
        "kill myself",
        "want to die",
        "end my life",
        "suicide",
        "take my own life",
    ],

    "SELF_HARM": [
        "cut myself",
        "self harm",
        "hurt myself",
        "harm myself",
    ],

    "HARM_TO_OTHERS": [
        "kill him",
        "kill her",
        "kill them",
        "hurt someone",
        "shoot someone",
        "attack someone",
    ],

    "ABUSE_OR_DANGER": [
        "being abused",
        "domestic violence",
        "being beaten",
        "being assaulted",
        "someone is hurting me",
    ],
}
