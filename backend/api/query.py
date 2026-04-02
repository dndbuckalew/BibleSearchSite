from fastapi import APIRouter, Response

from backend.models.query_decision import QueryDecision
from backend.models.query_models import QueryRequest
from backend.services.crisis_detector import detect_crisis  # Tier 0 import

router = APIRouter()

# Maximum number of clarification redirects allowed
MAX_REDIRECTS = 3

def infer_intent(question: str) -> str:
    q = question.lower().strip()

    # 1. Direct scripture detection (verses, chapters)
    if any(char.isdigit() for char in q):
        return "DISPLAY"

    # 2. Explicit personal reflection detection (strict only)
    personal_indicators = [
        "how do i",
        "what should i",
        "how can i",
        "i am struggling",
        "i'm struggling",
        "i feel",
        "help me deal",
        "how should i",
        "what do i do",
    ]

    if any(phrase in q for phrase in personal_indicators):
        return "REFLECT"

    # 3. Default → scripture pipeline
    return "DISPLAY"

def resolve_why_anchor(existing_anchor: str | None, question: str) -> str:
    if not existing_anchor:
        return question

    if len(question) < 12:
        return existing_anchor

    return question


# ------------------------------------------------------------
# CORS preflight — MUST exist for browsers
# ------------------------------------------------------------
@router.options("/api/query")
def options_query():
    return Response(status_code=200)


# ------------------------------------------------------------
# WHY gate
# ------------------------------------------------------------
@router.post("/api/query", response_model=QueryDecision)
def handle_query(req: QueryRequest):
    question = (req.question or "").strip()

    # ------------------------------------------------------------
    # Tier 0 — Deterministic Crisis Detection (Structural Only)
    # Must execute BEFORE intent inference or routing.
    # ------------------------------------------------------------
    crisis_detected, crisis_type, crisis_confidence = detect_crisis(question)

    why_anchor = resolve_why_anchor(None, question)

    if len(question) < 3:
        return QueryDecision(
            decision="REDIRECT",
            message=(
                "I want to walk with you in this reflection. "
                "Could you share a little more about what you’re seeking?"
            ),
            why_anchor=why_anchor,
            redirect_count=1,
            crisis_detected=crisis_detected,
            crisis_type=crisis_type,
            crisis_confidence=crisis_confidence,
        )

    intent = infer_intent(question)

    if intent in ("DISPLAY", "REFLECT"):
        return QueryDecision(
            decision="PROCEED",
            execution_payload={
                "question": req.question,
                "translation": req.translation,
                "persona": req.persona,
                "want_commentary": req.want_commentary,
            },
            why_anchor=why_anchor,
            crisis_detected=crisis_detected,
            crisis_type=crisis_type,
            crisis_confidence=crisis_confidence,
        )

    redirect_count = 1

    if redirect_count >= MAX_REDIRECTS:
        return QueryDecision(
            decision="STOP",
            message=(
                "I want to be careful not to assume too much. "
                "If you’d like, you can try rephrasing what you’re seeking, "
                "or choose a specific passage to explore."
            ),
            why_anchor=why_anchor,
            redirect_count=redirect_count,
            crisis_detected=crisis_detected,
            crisis_type=crisis_type,
            crisis_confidence=crisis_confidence,
        )

    return QueryDecision(
        decision="REDIRECT",
        message=(
            "I want to make sure I understand what you’re hoping to explore. "
            "Could you share a bit more about what’s prompting this question?"
        ),
        why_anchor=why_anchor,
        redirect_count=redirect_count,
        crisis_detected=crisis_detected,
        crisis_type=crisis_type,
        crisis_confidence=crisis_confidence,
    )

    
