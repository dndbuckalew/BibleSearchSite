# backend/models/audience/audience_models.py

from typing import Optional

from pydantic import BaseModel, Field


class AudienceRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)

    contact_type: str = Field(..., min_length=1)

    organization: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

    consent: bool = Field(default=False)

    source: str = Field(default="BTA-STAY-CONNECTED")


class AudienceResponse(BaseModel):
    success: bool
    message: str
    