# backend/services/concept_mapping_service.py

"""
Concept Mapping Service
Phase 9.1D.V2 — Controlled LLM Fallback Wrapper

Purpose:
Encapsulate LLM concept mapping so query_service.py remains
pure orchestration with no execution logic.
"""

from typing import List

from backend.core.linguistic.llm_concept_mapper import map_query_to_concepts
from backend.services.ai_client import call_ai_model


def map_concepts_with_llm(
    question: str,
    available_concepts: List[str],
) -> List[str]:
    """
    Controlled entry point for LLM concept mapping.

    Responsibilities:
    - Calls LLM via ai_client
    - Delegates mapping logic to llm_concept_mapper
    - Returns validated concept keys only

    Returns:
        List[str]: Valid concept keys (or empty list)
    """

    return map_query_to_concepts(
        question=question,
        available_concepts=available_concepts,
        llm_client=call_ai_model,
    )
    