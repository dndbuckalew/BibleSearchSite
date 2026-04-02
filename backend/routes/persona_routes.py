# backend/routes/persona_routes.py

from fastapi import APIRouter, HTTPException
from backend.models.persona_models import PersonaRequest, PersonaResponse
from backend.services.persona_service import PersonaService

router = APIRouter()
persona_service = PersonaService()


@router.post("/", response_model=PersonaResponse)
async def run_persona(request: PersonaRequest):
    """
    Execute persona-based reflection logic.
    """
    try:
        return persona_service.run_persona(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
