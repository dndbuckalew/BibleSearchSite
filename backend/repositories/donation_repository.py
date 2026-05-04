# backend/repositories/donation_repository.py

from backend.models.donation_models import DonationResponse


class DonationRepository:
    def __init__(self) -> None:
        self._store: dict[str, DonationResponse] = {}

    def save(self, donation: DonationResponse) -> DonationResponse:
        self._store[donation.transaction_id] = donation
        return donation

    def get(self, transaction_id: str) -> DonationResponse | None:
        return self._store.get(transaction_id)
             