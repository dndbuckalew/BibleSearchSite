# backend/services/donation_state_service.py

from backend.models.donation_models import DonationStatus


class DonationStateService:
    def next_status(self, current: DonationStatus, provider_status: str | None = None) -> DonationStatus:
        if current == DonationStatus.PENDING:
            return DonationStatus.QR_READY

        if current == DonationStatus.QR_READY and provider_status == "processing":
            return DonationStatus.PROCESSING

        if current == DonationStatus.PROCESSING and provider_status == "paid":
            return DonationStatus.COMPLETED

        if provider_status == "failed":
            return DonationStatus.FAILED

        if provider_status == "expired":
            return DonationStatus.EXPIRED

        return current
        