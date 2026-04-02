"""
Phase 9.1D.V2 — Controlled LLM Concept Mapper

Purpose:
Map a natural-language user question to EXISTING deterministic
vocabulary concepts only when deterministic vocabulary resolution fails.

Rules:
- Fallback only
- No new concept creation
- No scripture generation
- No theology
- No semantic interpretation layer changes
- Output must be strictly validated against existing concept registry
"""

from typing import List
import json

from backend.services.ai_client import call_ai_model


def _build_prompt(question: str, available_concepts: List[str]) -> str:
    concept_list = ", ".join(available_concepts)

    return f"""
You are mapping a user question to predefined vocabulary concepts.

Allowed concepts:
{concept_list}

User question:
{question}

Rules:
- Return ONLY concept names from the allowed concepts list
- Do NOT create new concepts
- Do NOT explain
- Do NOT add extra words
- Return at most 3 concepts
- Prefer the smallest number of concepts needed
- If nothing clearly matches, return an empty list

OUTPUT FORMAT:
Return STRICT JSON in this exact shape:

{{
  "concepts": ["concept1", "concept2"]
}}
""".strip()


def _parse_response(response_text: str) -> List[str]:
    if not response_text:
        return []

    clean = response_text.strip()

    try:
        if clean.startswith("```"):
            clean = clean.strip("`")
            clean = clean.replace("json", "", 1).strip()

        data = json.loads(clean)

        concepts = data.get("concepts", [])

        if isinstance(concepts, str):
            concepts = [concepts]

        if not isinstance(concepts, list):
            return []

        cleaned: List[str] = []
        for item in concepts:
            text = str(item).strip()
            if text:
                cleaned.append(text)

        return cleaned

    except Exception:
        # Secondary safe parse: comma-separated fallback only
        if "," in clean:
            return [part.strip() for part in clean.split(",") if part.strip()]

        # Single token fallback
        if clean:
            return [clean]

        return []


def _validate_concepts(
    candidate_concepts: List[str],
    available_concepts: List[str],
) -> List[str]:
    allowed = set(available_concepts)
    validated: List[str] = []
    seen = set()

    for concept in candidate_concepts:
        normalized = str(concept).strip()

        if not normalized:
            continue

        if normalized not in allowed:
            continue

        if normalized in seen:
            continue

        validated.append(normalized)
        seen.add(normalized)

        if len(validated) >= 3:
            break

    return validated


def map_query_to_concepts(
    question: str,
    available_concepts: List[str],
    llm_client=None,
) -> List[str]:
    """
    Map a user question to existing concept keys only.

    Behavior:
    - If llm_client is None -> returns []
    - If llm_client is provided -> prompt LLM with strict constraints
    - Output is validated against available_concepts
    - Returns max 3 concepts
    """
    if not question or not str(question).strip():
        return []

    if not available_concepts:
        return []

    if llm_client is None:
        return []

    prompt = _build_prompt(
        question=str(question).strip(),
        available_concepts=available_concepts,
    )

    try:
        if callable(llm_client):
            raw_response = llm_client(prompt)
        else:
            return []

        parsed = _parse_response(raw_response)
        return _validate_concepts(parsed, available_concepts)

    except Exception as e:
        print("LLM CONCEPT MAPPER ERROR:", str(e))
        return []
        