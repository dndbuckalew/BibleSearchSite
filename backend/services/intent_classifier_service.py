"""
Intent Classifier Service
Runtime Boundary Classification Layer

Purpose:
Provide a governed AI classification service that determines whether a
user's message should continue through the normal BTA theological
runtime or cross the constitutional boundary into the crisis
management workflow.

This service performs classification only.

It does not:
    • retrieve Scripture
    • generate responses
    • perform escalation
    • terminate processing

Its sole responsibility is to classify runtime intent so the
orchestrator (QueryService) can determine the appropriate execution
path.
"""
from backend.services.ai_client import call_ai_model

# intent_classifier_service.py

ALLOWED_INTENTS = {
    "SELF_HARM_RISK",
    "THEOLOGICAL_QUERY",
    "GENERAL_QUERY",
    "EMOTIONAL_DISTRESS",
}

def classify_intent(question: str) -> str:
    """
    Returns one of:
    SELF_HARM_RISK | THEOLOGICAL_QUERY | GENERAL_QUERY | EMOTIONAL_DISTRESS
    """

    prompt = f"""
    Classify the user's intent.

    Return ONLY valid JSON:
    {{ "intent": "SELF_HARM_RISK | THEOLOGICAL_QUERY | GENERAL_QUERY | EMOTIONAL_DISTRESS" }}

    Rules:
    - Theological questions about difficult topics are NOT crisis
    - Single words are NOT crisis
    - Only explicit or strongly implied self-harm intent = SELF_HARM_RISK
    - Do not explain
    - Do not add extra text

    User input:
    "{question}"
    """

    try:
        response = call_ai_model(prompt)

        # Simple safe parsing (temporary)
        for intent in ALLOWED_INTENTS:
            if intent in response:
                return intent

        return "GENERAL_QUERY"

    except Exception:
        return "GENERAL_QUERY"
