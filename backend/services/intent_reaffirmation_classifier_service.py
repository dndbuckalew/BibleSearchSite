"""
Intent Reaffirmation Classifier Service
Version 5.6 — Conversational Intent Classification Layer

Purpose:
Provide a governed AI classification service that identifies the
reader's conversational intent before intent reaffirmation.

This service performs classification only.

It does not:
    • generate reader responses
    • reaffirm understanding
    • retrieve Scripture
    • perform runtime routing
    • perform crisis escalation

Its sole responsibility is to classify the reader's conversational
intent so the Intent Reaffirmation Service can confirm understanding
before deeper semantic exploration.
"""

import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_reaffirmation_intent(user_message: str) -> dict:
    """
    Classify the reader's conversational intent.

    Returns:
        {
            "intent": "...",
            "confidence": 0.00-1.00
        }

    Returns None if classification fails.
    """

    prompt = f"""
Purpose

You are the Conversational Intent Classifier for Bible Therapy Assistant™.

Your sole responsibility is to identify what the reader is seeking so
their understanding may be reaffirmed before deeper exploration.

You are NOT:

• a response generator
• a Scripture retrieval engine
• a crisis classifier
• a theological interpreter

Return ONLY valid JSON in this format:

{{
    "intent": "<classification>",
    "confidence": <0.0 to 1.0>
}}

Valid intent classifications:

SEEKING_UNDERSTANDING
SEEKING_COMFORT
SEEKING_ENCOURAGEMENT
SEEKING_WISDOM
SEEKING_DIRECTION
SEEKING_FORGIVENESS
SEEKING_HOPE
SEEKING_CLARIFICATION
GENERAL_EXPLORATION

If uncertain, return GENERAL_EXPLORATION.

User Message:
\"\"\"
{user_message}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You classify conversational intent and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print("INTENT REAFFIRMATION CLASSIFIER ERROR:", str(e))
        return None
        