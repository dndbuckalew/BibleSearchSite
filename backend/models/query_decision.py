# Insert into backend/models/query_decision.py

from typing import Optional, Literal
from pydantic import BaseModel


DecisionType = Literal["REDIRECT", "PROCEED", "STOP"]


class QueryDecision(BaseModel):
    """
    Represents the outcome of intent evaluation in query.py.

    This model intentionally contains:
    - No scripture
    - No execution results
    - No service data

    It expresses only WHAT should happen next and WHY.
    """

    decision: DecisionType

    # User-facing message (voice)
    message: Optional[str] = None

    # Persistent reminder of what the user is exploring
    why_anchor: Optional[str] = None

    # How many redirects have occurred so far
    redirect_count: int = 0

    # Fully qualified execution instruction (only when decision == PROCEED)
    execution_payload: Optional[dict] = None

    # ------------------------------------------------------------
    # Tier 0 — Crisis Metadata (Structural Only)
    # ------------------------------------------------------------
    crisis_detected: bool = False
    crisis_type: Optional[str] = None
    crisis_confidence: Optional[str] = None
