# backend/models/donation_models.py

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DonationStatus(str, Enum):
    PENDING = "pending"
    QR_READY = "qr_ready"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class DonationRequest(BaseModel):
    amount: Optional[float] = Field(default=None, ge=1)
    currency: str = Field(default="USD")
    source: str = Field(default="donation_prompt")
    wants_receipt: bool = Field(default=False)
    donor_email: Optional[str] = None


class QRPayload(BaseModel):
    transaction_id: str
    donation_url: str
    payment_session_token: str
    expires_at: str


class DonationResponse(BaseModel):
    transaction_id: str
    status: DonationStatus
    qr_payload: QRPayload
    receipt_eligible: bool = False


class DonationCallbackRequest(BaseModel):
    transaction_id: str
    provider: str
    provider_status: str
    provider_reference: Optional[str] = None
    signature: Optional[str] = None


class ReceiptEligibility(BaseModel):
    transaction_id: str
    receipt_eligible: bool = False
    donor_email: Optional[str] = None
    