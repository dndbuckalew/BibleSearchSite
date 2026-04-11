# backend/services/ai_client.py

"""
AI Client
Phase 9.1D.2.8 — AI Meaning Integration Layer

Purpose:
Provide a single entry point for calling OpenAI to generate meaning.
"""

import os
from openai import OpenAI

# Initialize OpenAI client (clean, no custom transport)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_ai_model(prompt: str) -> str:
    """
    Calls OpenAI to generate meaning from Scripture.

    Returns:
        str: AI-generated response or None if failure
    """

    try:
        print("CALLING OPENAI MODEL")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a guide helping the reader understand the meaning of Scripture as it unfolds within the passage. "

                        "Do not give surface-level summaries or generalized statements. "

                        "Explain what is being revealed by the passage itself, allowing the meaning to develop clearly and naturally. "

                        "Let the explanation reflect the movement within the passage — what is happening, what tension or contrast may be present, "
                        "and how it leads toward understanding. "

                        "Stay grounded in the text. Do not introduce external interpretation or instruction. "

                        "Help the reader see why the passage matters by revealing what is already present within it."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()

        print("OPENAI RESPONSE:", content)

        return content

    except Exception as e:
        print("AI CLIENT ERROR TYPE:", type(e).__name__)
        print("AI CLIENT ERROR DETAIL:", str(e))
        return None
        