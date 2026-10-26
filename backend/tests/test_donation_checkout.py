"""Offline contract tests. No Stripe or database network calls are made."""

import os
import unittest
from unittest.mock import patch

import stripe
from fastapi import HTTPException

from backend.config.donation_config import DonationConfig, DonationConfigurationError
from backend.models.donation_models import DonationRequest
from backend.services.donation_service import DonationService
from backend.routes.donation_routes import create_donation


ENV = {
    "DONATION_ENV": "development",
    "STRIPE_SECRET_KEY": "sk_test_offline_fixture",
    "STRIPE_WEBHOOK_SECRET": "whsec_offline_fixture",
    "STRIPE_DONATION_PRICE_ID": "price_offline_fixture",
    "STRIPE_SUCCESS_URL": "http://127.0.0.1:3000/donation/success",
    "STRIPE_CANCEL_URL": "http://127.0.0.1:3000/",
}
PRICE = {"active": True, "livemode": False, "type": "one_time", "currency": "usd",
         "custom_unit_amount": {"minimum": 100, "preset": 500}}
SESSION = {"id": "cs_test_fixture", "url": "https://checkout.stripe.com/c/pay/cs_test_fixture",
           "expires_at": 2000000000, "livemode": False}


class DonationConfigurationTests(unittest.TestCase):
    def test_explicit_private_lan_return_origins_in_development_only(self):
        lan = {"BTA_DEV_LAN_ORIGIN": "http://192.168.0.32:3000",
               "STRIPE_SUCCESS_URL": "http://192.168.0.32:3000/donation/success",
               "STRIPE_CANCEL_URL": "http://192.168.0.32:3000/"}
        with patch.dict(os.environ, ENV | lan, clear=True):
            self.assertFalse(DonationConfig.load().live)
        for changes in [{"BTA_DEV_LAN_ORIGIN": ""},
                        {"BTA_DEV_LAN_ORIGIN": "http://8.8.8.8:3000"},
                        {"DONATION_ENV": "production", "STRIPE_SECRET_KEY": "sk_live_offline_fixture"}]:
            with self.subTest(changes=list(changes)), patch.dict(os.environ, ENV | lan | changes, clear=True):
                with self.assertRaises(ValueError):
                    DonationConfig.load()

    def test_loopback_development_uses_explicit_mode(self):
        with patch.dict(os.environ, ENV, clear=True):
            self.assertFalse(DonationConfig.load().live)

    def test_missing_or_invalid_config_fails_closed(self):
        cases = [
            {"DONATION_ENV": ""}, {"DONATION_ENV": "test"},
            {"STRIPE_SECRET_KEY": "sk_live_offline_fixture"}, {"STRIPE_SECRET_KEY": ""},
            {"STRIPE_DONATION_PRICE_ID": ""}, {"STRIPE_SUCCESS_URL": ""},
            {"STRIPE_SUCCESS_URL": "http://localhost.evil/donation/success"},
            {"STRIPE_SUCCESS_URL": "http://localhost:bad/donation/success"},
            {"STRIPE_CANCEL_URL": "http://localhost:3000/"},
            {"STRIPE_CANCEL_URL": "http://127.0.0.1:3000/donation/cancel"},
            {"STRIPE_SUCCESS_URL": "http://user:password@127.0.0.1:3000/donation/success"},
        ]
        for changes in cases:
            with self.subTest(changes=list(changes)), patch.dict(os.environ, ENV | changes, clear=True):
                with self.assertRaises(DonationConfigurationError):
                    DonationConfig.load()

    def test_production_requires_live_key_and_https(self):
        production = ENV | {"DONATION_ENV": "production", "STRIPE_SECRET_KEY": "sk_live_offline_fixture",
                            "STRIPE_SUCCESS_URL": "https://example.org/donation/success",
                            "STRIPE_CANCEL_URL": "https://example.org/"}
        with patch.dict(os.environ, production, clear=True):
            self.assertTrue(DonationConfig.load().live)
        for changes in [{"STRIPE_SECRET_KEY": ENV["STRIPE_SECRET_KEY"]},
                        {"STRIPE_SUCCESS_URL": "http://example.org/donation/success"},
                        {"STRIPE_SUCCESS_URL": "https://localhost/donation/success"}]:
            with self.subTest(changes=list(changes)), patch.dict(os.environ, production | changes, clear=True):
                with self.assertRaises(DonationConfigurationError):
                    DonationConfig.load()


class HostedCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, ENV, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.price = patch("stripe.Price.retrieve", return_value=stripe.StripeObject.construct_from(PRICE, None))
        self.retrieve = self.price.start()
        self.addCleanup(self.price.stop)
        self.session = patch("stripe.checkout.Session.create", return_value=stripe.StripeObject.construct_from(SESSION, None))
        self.create = self.session.start()
        self.addCleanup(self.session.stop)

    def test_hosted_checkout_passes_price_not_fixed_amount(self):
        result = DonationService().create_donation(DonationRequest(), "12345678-1234-4234-9234-123456789abc")
        args = self.create.call_args.kwargs
        self.assertEqual(args["line_items"], [{"price": ENV["STRIPE_DONATION_PRICE_ID"], "quantity": 1}])
        self.assertNotIn("ui_mode", args)  # Stripe default is hosted checkout.
        self.assertEqual(args["submit_type"], "donate")
        self.assertEqual(args["cancel_url"], ENV["STRIPE_CANCEL_URL"])
        self.assertTrue(args["success_url"].endswith("?session_id={CHECKOUT_SESSION_ID}"))
        self.assertEqual(args["client_reference_id"], result.transaction_id)
        self.assertEqual(args["payment_intent_data"]["metadata"]["transaction_id"], result.transaction_id)
        self.assertEqual(result.qr_payload.payment_session_token, SESSION["id"])
        self.assertEqual(args["idempotency_key"], result.transaction_id)
        self.assertNotIn("stripe_account", args)
        self.assertFalse({"transfer_data", "on_behalf_of", "application_fee_amount"} & args["payment_intent_data"].keys())

    def test_retry_preserves_transaction_identity(self):
        service = DonationService()
        request_id = "12345678-1234-4234-9234-123456789abc"
        first = service.create_donation(DonationRequest(), request_id)
        second = service.create_donation(DonationRequest(), request_id)
        self.assertEqual(first.transaction_id, second.transaction_id)
        self.assertEqual(self.create.call_args_list[0].kwargs, self.create.call_args_list[1].kwargs)

    def test_fixed_inactive_recurring_wrong_currency_and_live_prices_rejected(self):
        for changes in [{"custom_unit_amount": None}, {"active": False}, {"type": "recurring"},
                        {"currency": "eur"}, {"livemode": True}]:
            with self.subTest(changes=list(changes)):
                self.retrieve.return_value = stripe.StripeObject.construct_from(PRICE | changes, None)
                with self.assertRaises(DonationConfigurationError):
                    DonationService().create_donation(DonationRequest())
                self.create.assert_not_called()

    def test_live_key_rejected_before_any_stripe_call(self):
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_offline_fixture"}):
            with self.assertRaises(DonationConfigurationError):
                DonationService().create_donation(DonationRequest())
        self.retrieve.assert_not_called()
        self.create.assert_not_called()

    def test_development_initiation_does_not_require_webhook_setup(self):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            response = DonationService().create_donation(DonationRequest())
        self.assertEqual(response.qr_payload.payment_session_token, SESSION["id"])
        self.create.assert_called_once()

    def test_production_initiation_still_requires_webhook_setup(self):
        production = {"DONATION_ENV": "production", "STRIPE_SECRET_KEY": "sk_live_offline_fixture",
                      "STRIPE_SUCCESS_URL": "https://example.org/donation/success",
                      "STRIPE_CANCEL_URL": "https://example.org/", "STRIPE_WEBHOOK_SECRET": ""}
        with patch.dict(os.environ, production):
            with self.assertRaises(DonationConfigurationError):
                DonationService().create_donation(DonationRequest())
        self.retrieve.assert_not_called()
        self.create.assert_not_called()

    def test_unsigned_unconfigured_development_webhook_is_not_accepted(self):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            with self.assertRaises(DonationConfigurationError):
                DonationService().handle_webhook(b"{}", "invalid")

    def test_errors_do_not_expose_provider_details(self):
        self.retrieve.side_effect = stripe.APIConnectionError("sensitive provider error")
        with self.assertRaises(HTTPException) as caught:
            create_donation(DonationRequest(), None)
        self.assertEqual(caught.exception.status_code, 502)
        self.assertNotIn("sensitive", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
