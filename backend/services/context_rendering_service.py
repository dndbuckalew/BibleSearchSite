from typing import Optional

from backend.services.ai_client import call_ai_model


def render_context_frame(
    context_frame: Optional[str]
) -> Optional[str]:
    """
    Context Rendering Authority

    Shared infrastructure responsible for governed
    linguistic rendering of approved Context frames.
    """

    if context_frame is None:
        return None

    prompt = f"""
You are rendering CONTEXT for a Bible passage.

Your role is ONLY to improve how the context is expressed so the reader can better understand what is happening in the surrounding moment.

STRICT RULES:
- Do NOT explain meaning
- Do NOT interpret doctrine
- Do NOT teach or instruct
- Do NOT analyze the passage
- Do NOT expand beyond what is already described
- Do NOT introduce historical reconstruction or external facts

You may:
- Clarify what is happening
- Improve readability
- Make the scene more natural and understandable
- Slightly rephrase for better flow

Focus only on:
"What is happening here and what surrounding situation helps explain it?"

Context Frame:
{context_frame}

Return ONLY the improved contextual description.
"""

    try:
        result = call_ai_model(prompt)
        return result.strip() if result else context_frame
    except Exception:
        return context_frame
        