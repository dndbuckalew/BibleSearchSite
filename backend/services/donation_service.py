# backend/services/donation_service.py

from datetime import datetime, timedelta, UTC
from uuid import uuid4

from backend.models.donation_models import (
    DonationRequest,
    DonationResponse,
    DonationStatus,
    QRPayload,
)
from backend.repositories.donation_repository import DonationRepository
from backend.services.donation_receipt_service import DonationReceiptService

import stripe
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class DonationService:
    def __init__(self) -> None:
        self.repository = DonationRepository()
        self.receipt_service = DonationReceiptService()

    def create_donation(self, request: DonationRequest) -> DonationResponse:
        transaction_id = f"don_{uuid4().hex[:12]}"
        expires_at = datetime.now(UTC) + timedelta(minutes=30)
        stripe_key = os.getenv("STRIPE_SECRET_KEY", "")

        is_local = "localhost" in os.getenv("STRIPE_SUCCESS_URL", "")

        if is_local and not stripe_key.startswith("sk_test_"):
            raise ValueError("Local environment must use Stripe test key.")

        if not is_local and not stripe_key.startswith("sk_live_"):
            raise ValueError("Production environment must use Stripe live key.")
            
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Bibleta Donation",
                        },
                        "unit_amount": int(request.amount * 100),
                    },
                    "quantity": 1,
                }
            ],
            success_url=os.getenv("STRIPE_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL"),
        )

        qr_payload = QRPayload(
            transaction_id=transaction_id,
            donation_url=session.url,
            payment_session_token=session.id,
            expires_at=expires_at.isoformat(),
        )

        donation = DonationResponse(
            transaction_id=transaction_id,
            status=DonationStatus.QR_READY,
            qr_payload=qr_payload,
            receipt_eligible=self.receipt_service.evaluate(
                transaction_id=transaction_id,
                donor_email=request.donor_email if request.wants_receipt else None,
            ).receipt_eligible,
        )

        return self.repository.save(donation)
