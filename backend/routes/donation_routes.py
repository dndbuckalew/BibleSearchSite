# backend/routes/donation_routes.py

from fastapi import APIRouter

from backend.models.donation_models import (
    DonationRequest,
    DonationResponse,
    DonationCallbackRequest,
)
from backend.services.donation_service import DonationService

router = APIRouter(prefix="/donation", tags=["donation"])
donation_service = DonationService()


@router.post("/create", response_model=DonationResponse)
def create_donation(request: DonationRequest) -> DonationResponse:
    return donation_service.create_donation(request)

@router.post("/callback")
def donation_callback(payload: DonationCallbackRequest) -> dict:
    return {
        "transaction_id": payload.transaction_id,
        "provider": payload.provider,
        "provider_status": payload.provider_status,
        "accepted": True,
    }
