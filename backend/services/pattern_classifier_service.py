"""
Pattern Classifier Service
--------------------------

Phase 9.1D.2.2 — Semantic Pattern Verification

Purpose
-------
Determine the dominant communication pattern of a Scripture passage.

This service works with the deterministic linguistic pattern detector
and optionally uses an LLM to semantically verify the pattern.

Design
------
1. Linguistic engine produces candidate patterns.
2. This service verifies the correct pattern.
3. If no LLM is configured, it safely falls back to deterministic ranking.

Output
------
Returns a single pattern string.

Example:
    "promise"
"""

from typing import List, Optional


ALLOWED_PATTERNS = [
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


def build_pattern_prompt(text: str, candidate_patterns: List[str]) -> str:
    """
    Construct a controlled prompt for semantic classification.
    """

    candidate_list = ", ".join(candidate_patterns)

    prompt = f"""
You are analyzing a passage of Scripture.

Your task is to determine the dominant communication pattern.

Allowed patterns:
{", ".join(ALLOWED_PATTERNS)}

Candidate patterns detected by linguistic analysis:
{candidate_list}

Scripture text:
{text}

Rules:
- Choose ONLY one pattern from the allowed list
- Select the pattern that best describes the communication style
- Do not explain your answer
- Return only the pattern word
"""

    return prompt.strip()


def classify_pattern(
    text: str,
    candidate_patterns: List[str],
    llm_client=None
) -> str:
    """
    Determine dominant communication pattern.

    If no LLM is available, fallback to deterministic ranking.
    """

    if not candidate_patterns:
        return "teaching"

    # deterministic fallback
    if llm_client is None:
        return candidate_patterns[0]

    try:

        prompt = build_pattern_prompt(text, candidate_patterns)

        result = llm_client.generate(prompt)

        pattern = result.strip().lower()

        if pattern in ALLOWED_PATTERNS:
            return pattern

        return candidate_patterns[0]

    except Exception:
        return candidate_patterns[0]
    