# backend/services/donation_provider_service.py

class DonationProviderService:
    def build_handoff(self, transaction_id: str) -> dict:
        return {
            "provider": "stub",
            "provider_reference": f"prov_{transaction_id}",
        }
        