# backend/services/donation_email_service.py

class DonationEmailService:
    def build_receipt_trigger(self, transaction_id: str, donor_email: str) -> dict:
        return {
            "transaction_id": transaction_id,
            "to": donor_email,
            "from": "donations@bibleta.com",
            "trigger": "donation_receipt",
        }
        