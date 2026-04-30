# backend/routes/donation_routes.py

from fastapi import APIRouter

from backend.models.donation_models import (
    DonationRequest,
    DonationResponse,
    DonationCallbackRequest,
    DonationStatus,
)
from backend.services.donation_service import DonationService
from backend.services.donation_state_service import DonationStateService

router = APIRouter(prefix="/donation", tags=["donation"])
donation_service = DonationService()
state_service = DonationStateService()

@router.post("/create", response_model=DonationResponse)
def create_donation(request: DonationRequest) -> DonationResponse:
    return donation_service.create_donation(request)

@router.post("/callback")
def donation_callback(payload: DonationCallbackRequest) -> dict:
    return {
        "transaction_id": payload.transaction_id,
        "provider": payload.provider,
        "provider_status": payload.provider_status,
        "next_status": state_service.next_status(
            current=DonationStatus.PROCESSING,
            provider_status=payload.provider_status,
        ),
        "accepted": True,
    }
