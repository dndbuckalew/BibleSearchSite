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
            "name": request.name,
            "email": request.email,
            "contact_type": request.contact_type,
            "organization": request.organization,
            "city": request.city,
            "state": request.state,
            "consent": request.consent,
            "source": request.source,
            "submitted_at": submitted_at,
        }

        self.hubspot_service.create_contact(audience_record)

        return AudienceResponse(
            success=True,
            message="Audience information received successfully.",
        )
