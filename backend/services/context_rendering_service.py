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
    You are rendering CONTEXT for approved contextual information.

    Your role is ONLY to improve readability and clarity while preserving the contextual grounding already present in the Context Frame.

    CONTEXT AUTHORITY

    Context exists to help the reader understand the surrounding situation.

    Context may describe:

        * Participants
        * Circumstances
        * Events
        * Setting
        * Relevant surrounding conditions

    Context must NEVER:

        * Explain meaning
        * Explain significance
        * Explain implications
        * Explain lessons
        * Explain applications
        * Explain doctrine
        * Explain theology
        * Explain symbolism
        * Explain transformation
        * Provide conclusions
        * Summarize the message

    Avoid language that explains meaning, significance, implications, lessons, applications, doctrine, theology, symbolism, transformation, or conclusions.

    Examples of language to avoid include:
        * "This demonstrates..."
        * "This reveals..."
        * "This teaches..."
        * "This illustrates..."
        * "This reminds us..."
        * "This shows that..."
        * "This signifies..."
        * "This highlights the importance..."
        * "This invites readers..."

    You may:

        * Clarify what is happening
        * Improve readability
        * Improve sentence flow
        * Make the situation easier to understand
        * Remove repetitive phrasing
        * Reorganize wording for clarity

    You may NOT:

        * Add information not present in the Context Frame
        * Introduce new facts
        * Introduce new participants
        * Introduce new events
        * Introduce historical reconstruction
        * Introduce external knowledge
        * Expand beyond the supplied Context Frame

    Focus only on contextual grounding.

    Help the reader understand:

        * Participants
        * Circumstances
        * Events
        * Setting
        * Relevant surrounding conditions

    The reader should leave Context understanding the situation, not the interpretation.

    Context Frame:
    {context_frame}

    Return ONLY the improved contextual description.
    """

    try:
        result = call_ai_model(prompt)
        return result.strip() if result else context_frame
    except Exception:
        return context_frame
        