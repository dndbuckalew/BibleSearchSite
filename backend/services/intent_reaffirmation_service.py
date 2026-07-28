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

"""
Intent Reaffirmation Service

Purpose
-------
The purpose of this service is NOT to prove the AI understood the user's
request, nor to restate the user's words.

Instead, this service establishes the purpose and direction of the
conversation before knowledge is presented.

The generated opening answers the question:

    "Why are we about to explore this together?"

This creates a natural transition into Scripture (or other authoritative
knowledge sources) without making unsupported assumptions about the user's
precise intent.

Different interaction intents may produce different conversational openings.

Examples:

Informational
    "Love is one of the central themes of Scripture. Let's explore what the
     Bible reveals about God's love."

Research
    "John 3:16 is one of the most recognized verses in Scripture. Let's
     explore its meaning and context."

Emotional
    "I'm so sorry for your loss. Let's explore what Scripture says about
     comfort and hope during seasons of grief."

Safety
    "I'm glad you reached out. Let's focus first on helping you through
     what you're experiencing."

The objective is to establish the reader's journey—not to demonstrate the
AI's reasoning.
"""
"""
===============================================================================
Conversation Opening Service
===============================================================================

Architectural Purpose
---------------------

Despite the historical filename (intent_reaffirmation_service.py), the purpose
of this service is NOT to reaffirm that the AI correctly understood the
reader's request.

Early implementations attempted to generate responses such as:

    "If I understand correctly..."
    "You're asking about..."
    "It sounds like..."

While technically accurate, these openings made the conversation feel
mechanical and shifted attention toward the AI rather than the reader.

Human-Centered Conversation
---------------------------

This service now generates a single conversational opening that naturally
introduces the journey before Scripture is presented.

Its purpose is to align both the reader and the BTA around the subject of
exploration rather than validating the AI's interpretation.

The opening should:

• Feel natural in spoken conversation.
• Introduce the subject without teaching it.
• Avoid doctrinal interpretation.
• Avoid summarizing the Scripture.
• Avoid answering the reader's question.
• Avoid explaining historical context.
• Avoid AI-centric phrases such as
      "If I understand correctly..."
      "You're asking..."
      "It sounds like..."

Instead, it should simply begin the conversation.

Response Pipeline
-----------------

Conversation Opening
        ↓
Scripture (Authority)
        ↓
Summary (Primary Explanation / Deep Dive)
        ↓
Context
        ↓
Reflection

The Conversation Opening is intentionally limited to one natural sentence.

Scripture remains the authoritative foundation.

The Summary—not this service—is responsible for explaining the passage.

Context and Reflection continue the Progressive Disclosure journey.

HCGO Principle
--------------

The conversation begins by orienting the reader toward Scripture—not by
asking the reader to validate the AI.

This reflects the Human-Centered Governed Orchestration (HCGO) principle that
AI assists the reader's journey without becoming the focus of the conversation.
===============================================================================
"""

SYSTEM_PROMPT = """
You are the Intent Reaffirmation component of the HCGO Semantic Runtime.

Your responsibility is to generate the opening sentence of the reader's
journey before authoritative knowledge is presented.

You will receive:

• The reader's original question.
• A Conversation Context.

Before writing, silently determine:

    Why is this conversation worth having?

Do not state or reference that question.

Instead, write one natural sentence that establishes the significance of
the topic, concern, or experience being explored.

The sentence should feel like the natural beginning of a conversation
between two people.

Rules:

1. Maximum 20 words.
2. Sound warm and conversational.
3. Do not begin with:
   - If I understand correctly
   - I understand
   - It sounds like
   - You're asking
   - You're looking for
4. Do not restate the user's question.
5. Do not answer the question.
6. Do not quote Scripture.
7. Do not provide doctrine.
8. Do not provide advice.
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
    Conversation Context:
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
    