"""Offline Stripe-authoritative lifecycle tests. No database or network calls."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi import FastAPI
import stripe

from backend.models.donation_models import DonationRequest
from backend.routes.donation_routes import router
from backend.services.donation_service import DonationService, UnknownDonation
from test_donation_checkout import ENV, PRICE


def signed(payload, secret=ENV["STRIPE_WEBHOOK_SECRET"], timestamp=None):
    timestamp = int(time.time()) if timestamp is None else timestamp
    digest = hmac.new(secret.encode(), str(timestamp).encode() + b"." + payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


async def request(app, path, body, headers=None):
    payload = json.dumps(body).encode()
    sent = []
    consumed = False

    async def receive():
        nonlocal consumed
        if not consumed:
            consumed = True
            return {"type": "http.request", "body": payload, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    await app({"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
               "method": "POST", "scheme": "http", "path": path, "raw_path": path.encode(),
               "query_string": b"", "headers": [(b"content-type", b"application/json")] +
               [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
               "client": ("127.0.0.1", 10000), "server": ("test", 80)}, receive, send)
    start = next(item for item in sent if item["type"] == "http.response.start")
    content = b"".join(item.get("body", b"") for item in sent if item["type"] == "http.response.body")
    return start["status"], json.loads(content), dict(start["headers"])


class StripeAuthoritativeDonationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, ENV, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.service = DonationService()
        self.sessions = {}  # Fake remote Stripe state, not application persistence.

        def create(**kwargs):
            session_id = "cs_test_" + kwargs["client_reference_id"]
            data = self.sessions.setdefault(session_id, {
                "id": session_id, "object": "checkout.session", "livemode": False,
                "url": "https://checkout.stripe.com/c/pay/" + session_id,
                "expires_at": int(time.time()) + 1800, "mode": "payment", "status": "open",
                "payment_status": "unpaid", "client_reference_id": kwargs["client_reference_id"],
                "metadata": kwargs["metadata"], "payment_intent": None,
            })
            return stripe.StripeObject.construct_from(data, None)

        self.patches = [patch("stripe.Price.retrieve", return_value=stripe.StripeObject.construct_from(PRICE, None)),
                        patch("stripe.checkout.Session.create", side_effect=create),
                        patch("stripe.checkout.Session.retrieve", side_effect=lambda session_id, **kwargs: stripe.StripeObject.construct_from(self.sessions[session_id], None))]
        self.price, self.create, self.retrieve = [item.start() for item in self.patches]
        for item in self.patches:
            self.addCleanup(item.stop)
        self.response = self.service.create_donation(DonationRequest(), str(uuid4()))
        self.session_id = self.response.qr_payload.payment_session_token

    def pay(self):
        data = self.sessions[self.session_id]
        suffix = self.response.transaction_id
        data.update(status="complete", payment_status="paid", amount_total=1729, currency="usd",
                    payment_intent={"id": "pi_" + suffix, "livemode": False, "status": "succeeded", "currency": "usd",
                                    "amount_received": 1729, "metadata": data["metadata"],
                                    "latest_charge": {"id": "ch_" + suffix, "livemode": False, "paid": True,
                                                      "status": "succeeded", "currency": "usd", "amount": 1729,
                                                      "payment_intent": "pi_" + suffix,
                                                      "receipt_url": "https://pay.stripe.com/receipts/" + suffix}})

    def event(self, event_type="checkout.session.completed"):
        value = {"id": "evt_" + uuid4().hex, "object": "event", "type": event_type, "livemode": False,
                 "data": {"object": self.sessions[self.session_id]}}
        return json.dumps(value).encode()

    def test_verified_payment_and_receipt_without_repository(self):
        self.pay()
        result = self.service.reconcile(self.session_id)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["amount_total"], 1729)
        self.assertEqual(result["receipt_status"], "available")
        self.assertTrue(result["receipt_url"].startswith("https://pay.stripe.com/"))
        self.assertFalse(hasattr(self.service, "repository"))
        self.assertNotIn("email", result)

    def test_new_service_instance_reconciles_from_stripe_only(self):
        self.pay()
        self.assertEqual(self.service.reconcile(self.session_id), DonationService().reconcile(self.session_id))
        self.assertEqual(self.retrieve.call_count, 2)

    def test_concurrent_event_replays_are_read_only(self):
        self.pay()
        payload = self.event()
        signature = signed(payload)
        calls = self.create.call_count
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: DonationService().handle_webhook(payload, signature), range(4)))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertTrue(results[0]["accepted"])
        self.assertNotIn("duplicate", results[0])  # No durable deduplication claim.
        self.assertEqual(self.create.call_count, calls)
        self.assertEqual(self.retrieve.call_count, 4)

    def test_old_failure_event_reads_current_paid_stripe_state(self):
        payload = self.event("checkout.session.async_payment_failed")
        self.pay()
        result = self.service.handle_webhook(payload, signed(payload))
        self.assertEqual(result["status"], "completed")

    def test_failed_expired_and_pending_states_come_from_stripe(self):
        self.assertEqual(self.service.reconcile(self.session_id)["status"], "qr_ready")
        session = self.sessions[self.session_id]
        session.update(status="complete", payment_intent={"status": "processing"})
        self.assertEqual(self.service.reconcile(self.session_id)["status"], "processing")
        session["payment_intent"]["status"] = "requires_payment_method"
        self.assertEqual(self.service.reconcile(self.session_id)["status"], "failed")
        session["status"] = "expired"
        self.assertEqual(self.service.reconcile(self.session_id)["status"], "expired")

    def test_unpaid_return_is_not_success_or_receipt(self):
        result = self.service.reconcile(self.session_id)
        self.assertNotEqual(result["status"], "completed")
        self.assertIsNone(result["receipt_url"])

    def test_invalid_old_or_tampered_signatures_are_rejected(self):
        payload = self.event()
        for body, signature in [(payload, signed(payload, "wrong")),
                                (payload, signed(payload, timestamp=int(time.time()) - 1000)),
                                (payload + b" ", signed(payload))]:
            with self.assertRaises(stripe.SignatureVerificationError):
                self.service.handle_webhook(body, signature)
        self.retrieve.assert_not_called()

    def test_amount_mismatch_rejected_then_retry_succeeds(self):
        self.pay()
        self.sessions[self.session_id]["payment_intent"]["amount_received"] = 1
        payload = self.event()
        with self.assertRaises(ValueError):
            self.service.handle_webhook(payload, signed(payload))
        self.pay()
        self.assertEqual(self.service.handle_webhook(payload, signed(payload))["status"], "completed")

    def test_other_application_wrong_identity_and_mode_are_rejected(self):
        original = self.sessions[self.session_id]
        for changes in [{"metadata": original["metadata"] | {"application": "other"}},
                        {"metadata": original["metadata"] | {"corporate_entity": "other"}},
                        {"metadata": original["metadata"] | {"environment": "production"}},
                        {"client_reference_id": "other"}, {"livemode": True}]:
            self.sessions[self.session_id] = original | changes
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                self.service.reconcile(self.session_id)
        self.sessions[self.session_id] = original
        event = json.loads(self.event())
        event["livemode"] = True
        payload = json.dumps(event).encode()
        with self.assertRaises(ValueError):
            self.service.handle_webhook(payload, signed(payload))

    def test_legacy_sessions_require_manual_reconciliation(self):
        self.sessions[self.session_id]["metadata"] = {}
        with self.assertRaises(UnknownDonation):
            self.service.reconcile(self.session_id)

    def test_forged_receipt_and_payment_intent_are_rejected(self):
        self.pay()
        self.sessions[self.session_id]["payment_intent"]["latest_charge"]["receipt_url"] = "https://example.org/receipt"
        with self.assertRaises(ValueError):
            self.service.reconcile(self.session_id)
        self.pay()
        self.sessions[self.session_id]["payment_intent"]["latest_charge"]["payment_intent"] = "pi_other"
        with self.assertRaises(ValueError):
            self.service.reconcile(self.session_id)

    def test_unknown_syntax_or_live_session_never_queries_stripe_in_development(self):
        for session_id in ["invalid", "cs_live_fixture"]:
            with self.assertRaises(UnknownDonation):
                self.service.reconcile(session_id)
        self.retrieve.assert_not_called()

    def test_unrelated_signed_events_are_ignored(self):
        event = json.loads(self.event())
        event["data"]["object"]["metadata"]["application"] = "another_app"
        payload = json.dumps(event).encode()
        self.assertTrue(self.service.handle_webhook(payload, signed(payload))["ignored"])
        self.retrieve.assert_not_called()

    def test_lost_create_response_retry_uses_same_stripe_idempotency_key(self):
        attempt = str(uuid4())
        original = self.create.side_effect
        created = []
        def interrupted(**kwargs):
            created.append(original(**kwargs))
            raise stripe.APIConnectionError("Simulated lost response")
        self.create.side_effect = interrupted
        with self.assertRaises(stripe.APIConnectionError):
            self.service.create_donation(DonationRequest(), attempt)
        first_key = self.create.call_args.kwargs["idempotency_key"]
        self.create.side_effect = original
        response = DonationService().create_donation(DonationRequest(), attempt)
        self.assertEqual(response.qr_payload.payment_session_token, created[0].id)
        self.assertEqual(first_key, self.create.call_args.kwargs["idempotency_key"])

    def test_http_creation_signed_callback_and_confirmation(self):
        app = FastAPI()
        app.include_router(router)
        with patch("backend.routes.donation_routes.donation_service", self.service):
            headers = {"Idempotency-Key": str(uuid4())}
            status, created, response_headers = asyncio.run(request(app, "/donation/create", {"source": "donation_page"}, headers))
            self.assertEqual(status, 200)
            self.assertTrue(created["transaction_id"].startswith("bta_don_"))
            self.assertEqual(response_headers[b"cache-control"], b"no-store")
            status, retried, _ = asyncio.run(request(app, "/donation/create", {"source": "donation_page"}, headers))
            self.assertEqual(status, 200)
            self.assertEqual(created, retried)
            status, _, _ = asyncio.run(request(app, "/donation/callback", {"provider_status": "paid"}))
            self.assertEqual(status, 400)
            self.pay()
            event = json.loads(self.event())
            raw = json.dumps(event).encode()
            status, data, _ = asyncio.run(request(app, "/donation/webhook", event, {"Stripe-Signature": signed(raw)}))
            self.assertEqual(status, 200)
            self.assertTrue(data["accepted"])
            status, data, response_headers = asyncio.run(request(app, "/donation/verify", {"session_id": self.session_id}))
            self.assertEqual(status, 200)
            self.assertEqual(data["status"], "completed")
            self.assertEqual(response_headers[b"cache-control"], b"no-store")
            self.assertNotIn("email", data)
            with patch.object(self.service, "reconcile", side_effect=stripe.APIConnectionError("private provider details")):
                status, failure, _ = asyncio.run(request(app, "/donation/verify", {"session_id": self.session_id}))
                self.assertEqual(status, 502)
                self.assertNotIn("private", json.dumps(failure))


if __name__ == "__main__":
    unittest.main()
