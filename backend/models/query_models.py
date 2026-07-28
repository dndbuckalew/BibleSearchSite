from pydantic import BaseModel
from typing import List, Optional


# ------------------------------------------------------------
# Verse Item Model
# ------------------------------------------------------------
class VerseItem(BaseModel):
    reference: str
    text: str

    testament: Optional[str] = None
    book_order: Optional[int] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None


# ------------------------------------------------------------
# Query Request Model (WHY → WHAT contract)
# ------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str
    translation: Optional[str] = "kjv"
    persona: Optional[str] = None
    want_commentary: bool = False


# ------------------------------------------------------------
# Query Response Model (Render Contract)
# ------------------------------------------------------------
class QueryResponse(BaseModel):

    # Phase 9.1D.2.9 — Intent Reaffirmation
    # Reader reassurance that their intent has been understood.
    # Rendered before Scripture to establish reader confidence
    # before scriptural exploration begins.
    intent_reaffirmation: Optional[str] = None

    verses: List[VerseItem]
    summary: str

    commentary: Optional[str] = None
    context: Optional[str] = None
    context_exploration: Optional[str] = None
    reflection: Optional[str] = None

    # Phase 9.1A — Intent Echo (Render Gating Support)
    # Allows frontend render gating without inference.
    want_commentary: Optional[bool] = None

    # Phase 9.8B.5 — Escalation Flag (Structural Only)
    escalation_level: Optional[str] = None


# ------------------------------------------------------------
# Results Request Wrapper (WHAT execution endpoint)
# ------------------------------------------------------------
class ResultsRequest(BaseModel):
    execution_payload: dict
        
