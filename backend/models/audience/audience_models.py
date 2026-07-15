# backend/models/audience/audience_models.py

from typing import Optional

from pydantic import BaseModel, Field

class AudienceRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

    email: str = Field(..., min_length=1)

    contact_type: str = Field(..., min_length=1)

    organization: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    consent: bool = Field(default=False)

    hcgo_domain: str = Field(default="bta")

    source: str = Field(default="BTA-STAY-CONNECTED")

class AudienceResponse(BaseModel):
    success: bool
    status: str
    message: str
    