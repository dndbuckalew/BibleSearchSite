# backend/core/linguistic/llm_concept_mapper.py

"""
LLM Concept Mapper
Phase 9.1D.V2 — Controlled Vocabulary Mapping Layer

Purpose:
Translate user questions into existing concept keys using LLM,
while strictly enforcing deterministic system boundaries.

Guardrails:
- NO creation of new concepts
- ONLY return concepts from provided list
- MAX 3 concepts
- Return empty list on any failure
"""

from typing import List, Callable


def map_query_to_concepts(
    question: str,
    available_concepts: List[str],
    llm_client: Callable[[str], str],
) -> List[str]:
    """
    Maps a natural language question to existing concept keys.

    Args:
        question (str): User input
        available_concepts (List[str]): Allowed concept keys
        llm_client (Callable): AI call function

    Returns:
        List[str]: Validated concept keys (max 3)
    """

    if not question or not available_concepts:
        return []

    try:
        prompt = _build_prompt(question, available_concepts)

        response = llm_client(prompt)

        parsed = _parse_response(response)

        validated = _validate_concepts(parsed, available_concepts)

        return validated[:3]

    except Exception as e:
        print("LLM CONCEPT MAPPER ERROR:", str(e))
        return []


# ------------------------------------------------------------
# Prompt Builder
# ------------------------------------------------------------

def _build_prompt(question: str, concepts: List[str]) -> str:
    return f"""
You are mapping a user question to a fixed list of concept keys.

RULES:
- Only return concept keys from the provided list
- Do NOT create new concepts
- Do NOT explain anything
- Return ONLY a comma-separated list
- Maximum of 3 concepts

Available Concepts:
{", ".join(concepts)}

User Question:
{question}

Return:
"""


# ------------------------------------------------------------
# Response Parser
# ------------------------------------------------------------

def _parse_response(response: str) -> List[str]:
    if not response:
        return []

    parts = response.split(",")

    return [p.strip().lower() for p in parts if p.strip()]


# ------------------------------------------------------------
# Validation Layer
# ------------------------------------------------------------

def _validate_concepts(
    parsed: List[str],
    valid_concepts: List[str],
) -> List[str]:
    valid_set = set(valid_concepts)

    return [c for c in parsed if c in valid_set]
    