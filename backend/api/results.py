from fastapi import APIRouter

from backend.models.query_models import ResultsRequest, QueryResponse
from backend.services.query_service import QueryService

router = APIRouter()

# Instantiate service once (stateless usage per request)
query_service = QueryService()


@router.post("/api/results", response_model=QueryResponse)
def get_results(req: ResultsRequest):
    """
    Results execution endpoint (WHAT).

    Responsibilities:
    - Execute an already-approved query
    - Resolve scripture deterministically
    - Return verses and related outputs

    Non-responsibilities:
    - Intent detection
    - Guardrails
    - Clarification
    - Redirect logic

    This endpoint assumes the WHY gate (/api/query)
    has already approved execution.
    """
    return query_service.process_query(req.execution_payload)
