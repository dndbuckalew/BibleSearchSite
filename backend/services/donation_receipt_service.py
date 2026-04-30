# backend/services/donation_receipt_service.py

from backend.models.donation_models import ReceiptEligibility


class DonationReceiptService:
    def evaluate(self, transaction_id: str, donor_email: str | None) -> ReceiptEligibility:
        return ReceiptEligibility(
            transaction_id=transaction_id,
            receipt_eligible=bool(donor_email),
            donor_email=donor_email,
        )
        