"""Public checkout and capability-based confirmation; signed Stripe callbacks."""

from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
import stripe

from backend.config.donation_config import DonationConfigurationError
from backend.models.donation_models import DonationRequest, DonationResponse
from backend.services.donation_service import DonationService, UnknownDonation

router = APIRouter(prefix="/donation", tags=["donation"])
donation_service = DonationService()


def safe_call(function, *args):
    try:
        return function(*args)
    except DonationConfigurationError:
        raise HTTPException(status_code=503, detail="Donations are temporarily unavailable.") from None
    except UnknownDonation:
        raise HTTPException(status_code=404, detail="Donation not found. Please try again shortly.") from None
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid donation request.") from None
    except stripe.StripeError:
        raise HTTPException(status_code=502, detail="Unable to contact secure payment processing. Please try again.") from None



@router.post("/create", response_model=DonationResponse)
def create_donation(request: DonationRequest, idempotency_key: str | None = Header(default=None), response: Response = None) -> DonationResponse:
    if response is not None:
        response.headers["Cache-Control"] = "no-store"
    return safe_call(donation_service.create_donation, request, idempotency_key)


class VerificationRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=240)


@router.post("/verify")
def verify_donation(payload: VerificationRequest, response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    # Session ID is an unguessable bearer capability; never return donor contact data.
    return safe_call(donation_service.reconcile, payload.session_id)


@router.post("/callback")
@router.post("/webhook")
async def donation_callback(request: Request, stripe_signature: str | None = Header(default=None)):
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Stripe signature required.")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 262144:
            raise HTTPException(status_code=413, detail="Webhook payload too large.")
    return await run_in_threadpool(safe_call, donation_service.handle_webhook, bytes(body), stripe_signature)
