"""BTA Stripe Checkout, verified payment reconciliation, and signed events.

Only the account associated with the configured API key is used. No Connect,
banking, transfer, destination, or payout parameters are sent.
"""

from datetime import datetime, UTC
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

from dotenv import load_dotenv
import stripe

from backend.config.donation_config import DonationConfig, DonationConfigurationError
from backend.models.donation_models import DonationRequest, DonationResponse, DonationStatus, QRPayload

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
EVENTS = {"checkout.session.completed", "checkout.session.async_payment_succeeded",
          "checkout.session.async_payment_failed", "checkout.session.expired"}


class UnknownDonation(ValueError):
    pass


class DonationService:
    @staticmethod
    def webhook_secret():
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        if not secret.startswith("whsec_") or len(secret) <= 6:
            raise DonationConfigurationError("Stripe webhook verification must be configured.")
        return secret

    def create_donation(self, request: DonationRequest, idempotency_key: str | None = None) -> DonationResponse:
        config = DonationConfig.load()
        # Development can validate hosted test checkout before configuring event
        # delivery. Production still requires signing configuration; callbacks
        # always require a valid signature in either environment.
        if config.live:
            self.webhook_secret()
        if request.amount is not None or request.currency.upper() != "USD" or request.donor_email or request.wants_receipt:
            raise ValueError("Donation amount and email are collected only by Stripe.")
        attempt = str(UUID(idempotency_key)) if idempotency_key else str(uuid4())
        transaction_id = "bta_don_" + uuid5(NAMESPACE_URL, "bta:" + config.environment + ":" + attempt).hex

        price = stripe.Price.retrieve(config.price_id, api_key=config.secret_key).to_dict()
        if (not price.get("active") or price.get("livemode") != config.live
                or price.get("type") != "one_time" or price.get("currency") != "usd"
                or price.get("custom_unit_amount") is None):
            raise DonationConfigurationError("An active customer-chosen USD one-time Price in the correct mode is required.")
        metadata = {"transaction_id": transaction_id, "application": "bta",
                    "corporate_entity": "tad_concepts_llc", "environment": config.environment}
        session = stripe.checkout.Session.create(
            api_key=config.secret_key,
            idempotency_key=transaction_id,
            mode="payment",
            # Omit ui_mode: Stripe defaults to its hosted checkout. This avoids
            # relying on version-specific hosted/hosted_page enum spellings.
            submit_type="donate",
            payment_method_types=["card"],
            line_items=[{"price": config.price_id, "quantity": 1}],
            client_reference_id=transaction_id,
            metadata=metadata,
            payment_intent_data={"metadata": metadata},
            success_url=config.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=config.cancel_url,
        )
        destination = urlsplit(session.url or "")
        if session.livemode != config.live or destination.scheme != "https" or destination.netloc != "checkout.stripe.com":
            raise DonationConfigurationError("Checkout mode or destination mismatch.")
        return DonationResponse(
            transaction_id=transaction_id, status=DonationStatus.QR_READY,
            qr_payload=QRPayload(transaction_id=transaction_id, donation_url=session.url,
                                 payment_session_token=session.id,
                                 expires_at=datetime.fromtimestamp(session.expires_at, UTC).isoformat()),
            receipt_eligible=False,
        )

    def reconcile(self, session_id):
        config = DonationConfig.load()
        if not isinstance(session_id, str) or not re.fullmatch(r"cs_(test|live)_[A-Za-z0-9_]{1,220}", session_id):
            raise UnknownDonation("Unknown donation.")
        expected_prefix = "cs_live_" if config.live else "cs_test_"
        if not session_id.startswith(expected_prefix):
            raise UnknownDonation("Unknown donation.")
        session = stripe.checkout.Session.retrieve(session_id, api_key=config.secret_key,
                                                  expand=["payment_intent.latest_charge"]).to_dict()
        metadata = session.get("metadata") or {}
        transaction_id = metadata.get("transaction_id", "")
        if not re.fullmatch(r"bta_don_[a-f0-9]{32}", transaction_id):
            raise UnknownDonation("Unknown BTA donation.")
        expected = {"transaction_id": transaction_id, "application": "bta",
                    "corporate_entity": "tad_concepts_llc", "environment": config.environment}
        if (session.get("id") != session_id or session.get("livemode") != config.live
                or session.get("mode") != "payment" or session.get("client_reference_id") != transaction_id
                or any(metadata.get(key) != value for key, value in expected.items())):
            raise ValueError("Donation verification failed.")
        values = {"transaction_id": transaction_id, "status": "qr_ready",
                  "amount_total": None, "currency": None, "receipt_url": None, "receipt_status": "unavailable"}
        if session.get("status") == "expired":
            values["status"] = "expired"
        elif session.get("status") == "complete":
            values["status"] = "processing"
            intent = session.get("payment_intent")
            if isinstance(intent, dict) and intent.get("status") in {"canceled", "requires_payment_method"}:
                values["status"] = "failed"
        if session.get("payment_status") == "paid":
            intent = session.get("payment_intent") or {}
            charge = (intent.get("latest_charge") or {}) if isinstance(intent, dict) else {}
            amount = session.get("amount_total")
            if (not isinstance(intent, dict) or not isinstance(charge, dict)
                    or intent.get("status") != "succeeded" or intent.get("livemode") != config.live
                    or charge.get("livemode") != config.live or not charge.get("paid")
                    or charge.get("status") != "succeeded" or not charge.get("id") or not intent.get("id")
                    or charge.get("payment_intent") != intent.get("id")
                    or session.get("status") != "complete" or type(amount) is not int or amount <= 0
                    or session.get("currency") != "usd" or intent.get("currency") != "usd" or charge.get("currency") != "usd"
                    or intent.get("amount_received") != amount or charge.get("amount") != amount
                    or any((intent.get("metadata") or {}).get(key) != value for key, value in expected.items())):
                raise ValueError("Payment verification failed.")
            receipt = charge.get("receipt_url")
            if receipt:
                parsed = urlsplit(receipt)
                if parsed.scheme != "https" or parsed.netloc not in {"pay.stripe.com", "receipt.stripe.com"}:
                    raise ValueError("Invalid Stripe receipt.")
            values.update(status="completed", amount_total=amount, currency="usd", payment_intent_id=intent["id"],
                          charge_id=charge["id"], receipt_url=receipt, receipt_status="available" if receipt else "unavailable")
        return {key: values[key] for key in ("transaction_id", "status", "amount_total", "currency", "receipt_url", "receipt_status")}

    def handle_webhook(self, payload, signature):
        config = DonationConfig.load()
        event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret()).to_dict()
        if event.get("livemode") != config.live:
            raise ValueError("Webhook mode mismatch.")
        if event.get("type") not in EVENTS:
            return {"accepted": True, "ignored": True}
        obj = event.get("data", {}).get("object", {})
        if (obj.get("metadata") or {}).get("application") != "bta":
            return {"accepted": True, "ignored": True}
        if not event.get("id") or obj.get("object") != "checkout.session":
            raise ValueError("Invalid Stripe event.")
        # Ignore event-supplied payment assertions: retrieve current Stripe state.
        result = self.reconcile(obj.get("id"))
        # Read-only reconciliation has no local side effects to duplicate. There
        # is deliberately no claim of a durable processed-event registry.
        return {"accepted": True, "transaction_id": result["transaction_id"], "status": result["status"]}
