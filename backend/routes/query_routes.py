from fastapi import APIRouter, HTTPException
from backend.models.query_models import QueryRequest, QueryResponse
from backend.services.query_service import QueryService

router = APIRouter()
query_service = QueryService()

@router.post("/", response_model=QueryResponse)
async def query_scripture(req: QueryRequest):
    """
    Phase 7.x — Primary scripture + reflection query endpoint
    """
   
    try:
        return query_service.process_query(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
