"""
===============================================================================
HCGO Platform Service
Current Development Host: Bible Therapy Assistant (BTA)

Service: Intent Reaffirmation Service

Purpose:
Generate a brief, human-centered reaffirmation that communicates to the reader
that their conversational intent has been understood before Scripture is
presented.

Architectural Owner:
HCGO Orchestration Domain (Future)

ADR Reference:
ADR-003 – Semantic Runtime Architecture

Dependencies:
- intent_reaffirmation_classifier_service.py

Notes:
- This service consumes Conversational Intent Classification.
- This service performs no knowledge retrieval.
- This service performs no orchestration.
- This service performs no response assembly.
- This service owns only Intent Reaffirmation generation.
===============================================================================
"""

from backend.services.ai_client import call_ai_model


SYSTEM_PROMPT = """
You are the Intent Reaffirmation component of the HCGO Semantic Runtime.

Your responsibility is ONLY to reassure the reader that their question
has been understood.

You will receive:

• The reader's original question.
• A Conversational Intent Classification.

Use both to generate a brief, natural reaffirmation.

Rules:

1. Maximum 15 words.
2. Sound warm, natural, and human.
3. Never answer the question.
4. Never quote Scripture.
5. Never interpret doctrine.
6. Never provide advice.
7. Never summarize the future response.
8. Never apologize.
9. Never mention AI.
10. Return ONE sentence only.
"""


def generate_intent_reaffirmation(
    question: str,
    conversational_intent: str,
) -> str:
    """
    Generate a short Intent Reaffirmation.

    Args:
        question:
            Original Natural Language Query.

        conversational_intent:
            Conversational Intent Classification produced by
            intent_reaffirmation_classifier_service.py.

    Returns:
        Short reaffirmation string.
    """

    user_prompt = f"""
Conversational Intent:
{conversational_intent}

Reader Question:
{question}
"""

    prompt = f"""
{SYSTEM_PROMPT}

{user_prompt}
"""

    result = call_ai_model(prompt)

    return result.strip() if result else ""
    