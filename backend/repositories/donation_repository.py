# backend/repositories/donation_repository.py

from backend.models.donation_models import DonationResponse


class DonationRepository:
    def save(self, donation: DonationResponse) -> DonationResponse:
        return donation
        