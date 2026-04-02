# backend/services/ai_client.py

"""
AI Client
Phase 9.1D.2.8 — AI Meaning Integration Layer

Purpose:
Provide a single entry point for calling OpenAI to generate meaning.
"""

import os
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_ai_model(prompt: str) -> str:
    """
    Calls OpenAI to generate meaning from Scripture.

    Returns:
        str: AI-generated response
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # safe + available
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a guide who explains the meaning of Scripture clearly, "
                        "helping the reader understand what is being revealed and why it matters."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI CLIENT ERROR:", str(e))
        return ""
        