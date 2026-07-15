# backend/platform/integrations/hubspot/hubspot_service.py

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


class HubSpotService:
    def __init__(self) -> None:
        self.access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")

        self.base_url = "https://api.hubapi.com"

    def create_contact(self, audience_record: dict[str, Any]) -> dict[str, Any]:
        if not self.access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN is not configured.")

        url = f"{self.base_url}/crm/v3/objects/contacts"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "properties": {
                "firstname": audience_record.get("first_name"),
                "lastname": audience_record.get("last_name"),
                "email": audience_record.get("email"),
                "contact_type": audience_record.get("contact_type"),

                # AI-EP-001
                "company": audience_record.get("organization"),

                "city": audience_record.get("city"),
                "state": audience_record.get("state"),

                "consent": audience_record.get("consent"),
                "hcgo_domain": audience_record.get("hcgo_domain"),

                "source": audience_record.get("source"),
                "submitted_at": audience_record.get("submitted_at"),
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10,
        )

        if response.status_code == 409:
            return {
                "status": "existing_contact",
                "message": (
                    "This email address is already connected with "
                    "Bible Therapy Assistant™. Each email address "
                    "can only be associated with one contact. "
                    "Would you like to update the information "
                    "associated with this email address?"
                ),
            }

        if not response.ok:
            response.raise_for_status()

        return response.json()
