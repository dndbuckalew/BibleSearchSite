# backend/routes/audience/audience_routes.py

from fastapi import APIRouter

from backend.models.audience.audience_models import (
    AudienceRequest,
    AudienceResponse,
)
from backend.services.audience.audience_service import AudienceService

router = APIRouter(prefix="/audience", tags=["audience"])

audience_service = AudienceService()


@router.post("/stay-connected", response_model=AudienceResponse)
def stay_connected(request: AudienceRequest) -> AudienceResponse:
    return audience_service.process_audience(request)
    