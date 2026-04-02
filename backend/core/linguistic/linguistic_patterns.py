"""
Universal Linguistic Pattern Framework
--------------------------------------

Phase 9.1D.2.1 — BTA Linguistic Backbone
"""

from collections import defaultdict
from typing import List, Tuple
import re


# ---------------------------------------------------------
# Linguistic Pattern Definitions (12 Core Patterns)
# ---------------------------------------------------------

LINGUISTIC_PATTERNS = [

    "narrative",
    "teaching",
    "promise",
    "command",
    "warning",
    "revelation",
    "wisdom",
    "contrast",
    "invitation",
    "praise",
    "prayer",
    "prophecy"

]


# ---------------------------------------------------------
# Linguistic Signal Indicators
# ---------------------------------------------------------

PATTERN_SIGNALS = {

    "narrative": [
        "went",
        "came",
        "said",
        "answered",
        "saw"
    ],

    "teaching": [
        "whoever",
        "therefore",
        "let",
        "if"
    ],

    "promise": [
        "i will",
        "shall",
        "will not",
        "i am with"
    ],

    "command": [
        "do not",
        "go",
        "follow",
        "love",
        "believe"
    ],

    "warning": [
        "beware",
        "lest",
        "woe",
        "perish"
    ],

    "revelation": [
        "i am",
        "son of",
        "kingdom of"
    ],

    "wisdom": [
        "wise",
        "fool",
        "better than"
    ],

    "contrast": [
        "but",
        "rather"
    ],

    "invitation": [
        "come",
        "ask",
        "seek",
        "knock"
    ],

    "praise": [
        "praise",
        "glory",
        "bless the lord"
    ],

    "prayer": [
        "o lord",
        "hear my prayer"
    ],

    "prophecy": [
        "it shall come to pass",
        "in that day"
    ]

}


# ---------------------------------------------------------
# Combine Verse Text
# ---------------------------------------------------------

def combine_verse_text(verses) -> str:

    return " ".join(v.text for v in verses if v.text)


# ---------------------------------------------------------
# Linguistic Pattern Detection
# ---------------------------------------------------------

def detect_linguistic_patterns(text: str) -> List[Tuple[str, int]]:

    scores = defaultdict(int)

    text_lower = text.lower()

    for pattern, signals in PATTERN_SIGNALS.items():

        for signal in signals:

            # word boundary safe detection
            regex = r"\b" + re.escape(signal) + r"\b"

            matches = re.findall(regex, text_lower)

            if matches:
                scores[pattern] += len(matches)

    ranked_patterns = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_patterns   
    