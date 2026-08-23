from typing import Optional

from backend.services.ai_client import call_ai_model


def render_summary_lead_in(
    question: str,
    summary_frame: str
) -> Optional[str]:
    """
    Summary Rendering Authority

    Rewrites the deterministic Summary Frame as a short, conversational
    lead-in that picks up directly from the reader's own question —
    e.g. question "How does Jesus think about love?" becomes a summary
    that opens with "Jesus thinks about love...". It may only rephrase
    the meaning already present in the Summary Frame, never add to it.
    """

    if not summary_frame:
        return summary_frame

    prompt = f"""
    You are rendering a SUMMARY as a conversational lead-in that answers the reader's own question.

    Reader's Question:
    {question}

    Summary Frame (the only meaning you may draw from):
    {summary_frame}

    Your task:
    Rewrite the Summary Frame as one or two short sentences that read like the
    natural start of a reply to the reader's question — picking up the wording
    of the question itself where it fits naturally, rather than starting a
    generic description of "this passage."

    For example, if the question is "How does Jesus think about love?", a
    good opening reads like "Jesus speaks of love as..." rather than
    "This passage discusses love."

    You may:
        * Reuse phrasing from the question to open the sentence
        * Rephrase the Summary Frame for a more natural, spoken tone
        * Reorganize wording for clarity

    You may NOT:
        * Add meaning, claims, or theology not present in the Summary Frame
        * Invent details not grounded in the Summary Frame
        * Exceed two sentences

    Return ONLY the rewritten summary.
    """

    try:
        result = call_ai_model(prompt)
        return result.strip() if result else summary_frame
    except Exception:
        return summary_frame
