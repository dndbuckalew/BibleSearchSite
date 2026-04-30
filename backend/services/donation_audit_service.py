# backend/services/donation_audit_service.py

from datetime import datetime, UTC


class DonationAuditService:
    def record(self, transaction_id: str, event: str) -> dict:
        return {
            "transaction_id": transaction_id,
            "event": event,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        