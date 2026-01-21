# backend/routes/query_routes.py

from fastapi import APIRouter, HTTPException
from backend.models.query_models import QueryRequest, QueryResponse
from backend.services.query_service import QueryService
from backend.config.feature_flags import FEATURE_FLAGS

router = APIRouter()
query_service = QueryService()


@router.post("/", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """
    Production route for running Bible queries.
    """

    # Phase 3.1 — Step 3: Feature flag guard (ENABLE_PERSONAS)
    if not FEATURE_FLAGS.get("ENABLE_PERSONAS", True):
        return QueryResponse(
            verses=[],
            summary="Personas are currently disabled (feature flag ENABLE_PERSONAS is OFF).",
            commentary=""
        )

    try:
        response = query_service.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

