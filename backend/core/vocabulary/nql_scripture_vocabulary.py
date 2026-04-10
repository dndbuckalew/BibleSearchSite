# Insert into: backend/core/vocabulary/nql_scripture_vocabulary.py

"""
Phase 9.1D.V — NQL Vocabulary Expansion & Semantic Mapping

Deterministic concept-to-scripture mapping for NQL queries.

Vocabulary layer only.

No HTTP.
No persona.
No escalation logic.
No reflection logic.
No feature flags.
No schema changes.
No LLM.
No emotional inference.
No routing modification.

Design goals:
- Preserve deterministic behavior
- Support real-world user phrasing
- Improve normalization without introducing AI inference
- Expand concept coverage without creating unbounded word lists
"""

from typing import Dict, List, Set
import re

# ============================================================
# SIGNAL DEFINITIONS (Phase 9.1E — Step 4.1)
# ------------------------------------------------------------
# Purpose:
# Define small, stable linguistic signal groups used for
# structural detection of user intent.
#
# IMPORTANT:
# - These are NOT exhaustive word lists
# - These represent linguistic roles (not coverage)
# - These are intentionally small and controlled
# - No behavior change in this step
# ============================================================

# Question intent (user is asking something)
QUESTION_SIGNALS = {
    "why",
    "what",
    "how",
    "where",
    "when",
}

# Personal reference (self-related language)
PERSONAL_SIGNALS = {
    "i",
    "me",
    "my",
    "myself",
    "we",
    "us",
    "our",
}

# Divine reference (references to God)
DIVINE_SIGNALS = {
    "god",
    "lord",
    "jesus",
    "christ",
}

# Existence / creation signals
EXISTENCE_SIGNALS = {
    "exist",
    "exists",
    "here",
    "made",
    "create",
    "created",
    "purpose",
    "reason",
}

# Emotional indicators (non-diagnostic, signal only)
EMOTION_SIGNALS = {
    "lost",
    "afraid",
    "scared",
    "anxious",
    "worried",
    "confused",
    "alone",
}

# Life / behavior / direction signals
LIVING_SIGNALS = {
    "live",
    "life",
    "walk",
    "follow",
    "obey",
    "do",
    "doing",
    "should",
}

# ------------------------------------------------------------
# Controlled Input Normalization
# ------------------------------------------------------------

COMMON_MISSPELLINGS: Dict[str, str] = {
    "foregiveness": "forgiveness",
    "forgive ness": "forgiveness",
    "purpsoe": "purpose",
    "charactor": "character",
    "godlylife": "godly life",
}


def normalize_question(question: str) -> str:
    """
    Apply lightweight deterministic normalization.

    Supported:
    - lowercase
    - punctuation removal
    - whitespace normalization
    - controlled misspelling correction

    Not supported:
    - fuzzy matching
    - semantic inference
    - probabilistic guessing
    """
    if not question:
        return ""

    q = question.lower().strip()

        # Replace punctuation with spaces
    q = re.sub(r"[^a-z0-9\s]", " ", q)

    # Normalize internal whitespace
    q = re.sub(r"\s+", " ", q).strip()

    # Controlled full-string misspelling corrections
    if q in COMMON_MISSPELLINGS:
        q = COMMON_MISSPELLINGS[q]

    # Controlled token-level corrections
    tokens = q.split()
    corrected_tokens = [COMMON_MISSPELLINGS.get(token, token) for token in tokens]

    q = " ".join(corrected_tokens)
    q = re.sub(r"\s+", " ", q).strip()

    return q

# ============================================================
# SIGNAL EXTRACTION (Phase 9.1E — Step 4.2)
# ============================================================

def extract_signals(q: str) -> Dict[str, bool]:
    tokens = set(q.split())

    return {
        "question": any(token in QUESTION_SIGNALS for token in tokens),
        "personal": any(token in PERSONAL_SIGNALS for token in tokens),
        "divine": any(token in DIVINE_SIGNALS for token in tokens),
        "existence": any(token in EXISTENCE_SIGNALS for token in tokens),
        "emotion": any(token in EMOTION_SIGNALS for token in tokens),
        "living": any(token in LIVING_SIGNALS for token in tokens),
    }

# ============================================================
# CONCEPT RULE ENGINE (Phase 9.1E — Step 4.3)
# ============================================================

def detect_concepts_from_signals(q: str) -> List[str]:
    signals = extract_signals(q)

    concepts: List[str] = []

    # --------------------------------------------------------
    # PURPOSE (Initial Concept)
    # --------------------------------------------------------
    if (
        signals["question"]
        and signals["personal"]
        and (signals["divine"] or signals["existence"])
    ):
        concepts.append("purpose")

     # --------------------------------------------------------
    # FEAR (Initial Expansion)
    # --------------------------------------------------------
    if (
        signals["emotion"]
        and signals["personal"]
        and signals["question"]
    ):
        concepts.append("fear")

    return concepts

def contains_phrase(q: str, phrase: str) -> bool:
    """
    Deterministic whole-phrase containment.
    """
    return phrase in q


def contains_any(q: str, fragments: List[str]) -> bool:
    """
    Deterministic fragment containment.
    """
    return any(fragment in q for fragment in fragments)


def contains_all_tokens(q: str, required_tokens: List[str]) -> bool:
    """
    Deterministic all-token presence check.
    """
    tokens = set(q.split())
    return all(token in tokens for token in required_tokens)


# ------------------------------------------------------------
# Deterministic Concept Registry
# ------------------------------------------------------------

CONCEPT_REGISTRY: Dict[str, Dict[str, object]] = {
    # ---- Fear / Anxiety Roots ----
    "fear": {
        "description": "Concept related to fear or being fearful.",
        "match_any": ["fear", "fearful"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Isaiah 41:10",
            "2 Timothy 1:7",
            "Psalm 56:3",
        ],
    },
    "afraid": {
        "description": "Concept related to being afraid.",
        "match_any": ["afraid"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Joshua 1:9",
            "Isaiah 43:1",
            "Deuteronomy 31:6",
        ],
    },
    "anxiety": {
        "description": "Concept associated with anxiety.",
        "match_any": ["anxiety", "anxious"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Philippians 4:6-7",
            "1 Peter 5:7",
            "Matthew 6:34",
        ],
    },
    "sadness": {
        "description": "Concept associated with sadness or sorrow.",
        "match_any": ["sad", "sadness", "sorrow"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Psalm 34:18",
            "Matthew 5:4",
            "Revelation 21:4"
        ],
    },
    "anger": {
        "description": "Concept associated with anger, wrath, or frustration.",
        "match_any": ["anger", "angry", "wrath", "frustrated"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Ephesians 4:26",
            "James 1:19-20",
            "Proverbs 14:29"
        ],
    },
    # ---- Joy / Rejoicing ----
    "joy": {
        "description": "Concept associated with joy.",
        "match_any": ["joy"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Nehemiah 8:10",
            "John 15:11",
            "Romans 15:13",
        ],
    },
    "rejoice": {
        "description": "Concept associated with rejoicing.",
        "match_any": ["rejoice", "rejoicing"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Philippians 4:4",
            "Psalm 118:24",
            "1 Thessalonians 5:16",
        ],
    },

    # ---- Foundational Themes ----
    "hope": {
        "description": "Concept related to hope.",
        "match_any": ["hope", "hopeful"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Romans 15:13",
            "Jeremiah 29:11",
            "Hebrews 11:1",
        ],
    },
    "faith": {
        "description": "Concept associated with faith.",
        "match_any": ["faith"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Hebrews 11:6",
            "2 Corinthians 5:7",
            "Romans 10:17",
        ],
    },
    "trust": {
        "description": "Concept associated with trust.",
        "match_any": ["trust", "trusted"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Proverbs 3:5-6",
            "Psalm 37:5",
            "Psalm 9:10",
        ],
    },
    "peace": {
        "description": "Concept associated with peace.",
        "match_any": ["peace"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "John 14:27",
            "Philippians 4:7",
            "Isaiah 26:3",
        ],
    },
    "strength": {
        "description": "Concept associated with strength.",
        "match_any": ["strength", "strong"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Isaiah 40:31",
            "Philippians 4:13",
            "Psalm 28:7",
        ],
    },
    "love": {
        "description": "Concept associated with love.",
        "match_any": ["love"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "1 Corinthians 13:4-7",
            "John 3:16",
            "Romans 5:8",
        ],
    },
    "grace": {
        "description": "Concept associated with grace.",
        "match_any": ["grace"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Ephesians 2:8-9",
            "2 Corinthians 12:9",
            "Romans 3:24",
        ],
    },
    "forgiveness": {
        "description": "Concept associated with forgiveness.",
        "match_any": ["forgive", "forgiveness"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Matthew 18:21-22",
            "Ephesians 4:32",
            "1 John 1:9",
        ],
    },
    "suffering": {
        "description": "Concept associated with suffering or pain.",
        "match_any": ["suffering", "pain"],
        "match_phrases": [],
        "match_all_tokens": [],
        "scriptures": [
            "Romans 8:18",
            "Psalm 34:19",
            "2 Corinthians 4:16-18",
        ],
    },

    # ---- Expanded Abstract / Real-World Query Concepts ----
    "purpose": {
        "description": "Concept associated with purpose, design, or why a person exists.",
        "match_any": ["purpose"],
        "match_phrases": [
            "purpose of life",
            "why did god make me",
            "why did he make us",
            "why did god make us",
            "why are we here",
            "what is our purpose",
            "what is my purpose",
            "main purpose",
            "why was i made",
            "why were we made",
        ],
        "match_all_tokens": [
            ["why", "make", "me"],
            ["why", "made", "me"],
            ["our", "purpose"],
            ["my", "purpose"],
        ],
        "scriptures": [
            "Jeremiah 29:11",
            "Ephesians 2:10",
            "Proverbs 19:21",
        ],
    },
    "god_character": {
        "description": "Concept associated with who God is and what God is like.",
        "match_any": [],
        "match_phrases": [
            "who is god",
            "what is god like",
            "what kind of god",
            "god s character",
            "gods character",
            "character of god",
        ],
        "match_all_tokens": [
            ["who", "god"],
            ["what", "god", "like"],
        ],
        "scriptures": [
            "Exodus 34:6-7",
            "Psalm 145:8-9",
            "1 John 4:8",
        ],
    },
    "christian_living": {
        "description": "Concept associated with living a godly life and what God desires from a person.",
        "match_any": ["godly"],
        "match_phrases": [
            "how to live a godly life",
            "how do i live a godly life",
            "how should i live",
            "what does god want from me",
            "how does god want me to live",
            "live for god",
        ],
        "match_all_tokens": [
            ["how", "live"],
            ["god", "want", "me"],
            ["god", "want", "from", "me"],
        ],
        "scriptures": [
            "Micah 6:8",
            "Romans 12:1-2",
            "Colossians 3:12-17",
        ],
    },
    "betrayal": {
        "description": "Concept associated with betrayal, being betrayed, or treachery.",
        "match_any": ["betray"],
        "match_phrases": [
            "being betrayed",
            "was betrayed",
        ],
        "match_all_tokens": [],
        "scriptures": [
            "Psalm 41:9",
            "Matthew 26:14-16",
            "Luke 22:47-48",
        ],
    },
}


# ------------------------------------------------------------
# Deterministic Concept Resolution
# ------------------------------------------------------------

def match_concept(q: str, concept_data: Dict[str, object]) -> bool:
    """
    Determine whether a normalized question matches a concept.
    """
    match_any = concept_data.get("match_any", [])
    match_phrases = concept_data.get("match_phrases", [])
    match_all_tokens = concept_data.get("match_all_tokens", [])

    if match_any and contains_any(q, match_any):
        return True

    for phrase in match_phrases:
        if contains_phrase(q, phrase):
            return True

    for token_group in match_all_tokens:
        if contains_all_tokens(q, token_group):
            return True

    return False


def resolve_nql_topics(question: str) -> List[str]:
    """
    Deterministically resolves NQL concepts to scripture references.

    Guarantees:
    - No LLM
    - No probabilistic weighting
    - No routing modification
    - No semantic inference outside configured concept rules
    - Deterministic deduplicated output
    """
    if not question:
        return []

    q = normalize_question(question)

    # ------------------------------------------------------------
    # Step 1: Signal-Based Concept Detection (Phase 9.1E)
    # ------------------------------------------------------------
    signal_concepts = detect_concepts_from_signals(q)

    # Step 1: Try signal-based detection
    if signal_concepts:
        matched_concepts = signal_concepts
    else:
        matched_concepts: List[str] = []

        # Preserve registry order for deterministic output stability
        for concept, data in CONCEPT_REGISTRY.items():
            if match_concept(q, data):
                matched_concepts.append(concept)
    results: List[str] = []
    seen: Set[str] = set()

    for concept in matched_concepts:
        scriptures = CONCEPT_REGISTRY[concept]["scriptures"]
        for scripture in scriptures:
            if scripture not in seen:
                results.append(scripture)
                seen.add(scripture)

    return results
     