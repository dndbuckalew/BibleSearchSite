# backend/services/audience/audience_service.py

from datetime import datetime, UTC

from backend.models.audience.audience_models import (
    AudienceRequest,
    AudienceResponse,
)

from backend.platform.integrations.hubspot.hubspot_service import HubSpotService

class AudienceService:
    def __init__(self) -> None:
        self.hubspot_service = HubSpotService()

    def process_audience(self, request: AudienceRequest) -> AudienceResponse:
        submitted_at = datetime.now(UTC).isoformat()

        audience_record = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "contact_type": request.contact_type,
            "organization": request.organization,
            "city": request.city,
            "state": request.state,
            "consent": request.consent,
            "hcgo_domain": request.hcgo_domain,
            "source": request.source,
            "submitted_at": submitted_at,
        }

        hubspot_result = self.hubspot_service.create_contact(audience_record)

        if hubspot_result.get("status") == "existing_contact":
            return AudienceResponse(
                success=True,
                status="existing_contact",
                message=hubspot_result["message"],
            )

        return AudienceResponse(
            success=True,
            status="new_contact",
            message="Welcome to Bible Therapy Assistant™! Thank you for staying connected. We look forward to sharing future updates, new features, and resources with you.",
        )
