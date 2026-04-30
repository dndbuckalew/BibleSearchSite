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

class DonationService:
    def __init__(self) -> None:
        self.repository = DonationRepository()

    def create_donation(self, request: DonationRequest) -> DonationResponse:
        transaction_id = f"don_{uuid4().hex[:12]}"
        expires_at = datetime.now(UTC) + timedelta(minutes=30)

        qr_payload = QRPayload(
            transaction_id=transaction_id,
            donation_url=f"/donate/{transaction_id}",
            payment_session_token=uuid4().hex,
            expires_at=expires_at.isoformat(),
        )

        donation = DonationResponse(
            transaction_id=transaction_id,
            status=DonationStatus.QR_READY,
            qr_payload=qr_payload,
            receipt_eligible=bool(request.wants_receipt and request.donor_email),
        )

        return self.repository.save(donation)
        