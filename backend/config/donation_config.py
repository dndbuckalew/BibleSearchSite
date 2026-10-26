"""Fail-closed Stripe configuration, independent of Scripture/HubSpot settings."""

from dataclasses import dataclass, field
import os
from urllib.parse import urlsplit
from backend.config.development_network import development_frontend_origins


class DonationConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class DonationConfig:
    environment: str
    secret_key: str = field(repr=False)
    price_id: str
    success_url: str
    cancel_url: str

    @property
    def live(self) -> bool:
        return self.environment == "production"

    @classmethod
    def load(cls) -> "DonationConfig":
        environment = os.getenv("DONATION_ENV", "")
        key = os.getenv("STRIPE_SECRET_KEY", "")
        if environment not in {"development", "production"}:
            raise DonationConfigurationError("Set DONATION_ENV explicitly.")
        prefix = "sk_live_" if environment == "production" else "sk_test_"
        if not key.startswith(prefix) or len(key) <= len(prefix):
            raise DonationConfigurationError("Stripe credential mode does not match donation environment.")
        price = os.getenv("STRIPE_DONATION_PRICE_ID", "")
        if not price.startswith("price_"):
            raise DonationConfigurationError("Customer-chosen donation Price is required.")
        success = os.getenv("STRIPE_SUCCESS_URL", "")
        cancel = os.getenv("STRIPE_CANCEL_URL", "")
        for value, path in [(success, "/donation/success"), (cancel, "/")]:
            try:
                parsed = urlsplit(value)
                parsed.port  # Validate malformed port values as well.
            except ValueError as exc:
                raise DonationConfigurationError("Invalid donation return URL.") from exc
            local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
            secure = parsed.scheme == "https"
            development_origin = (environment == "development" and parsed.scheme == "http"
                                  and (local or f"{parsed.scheme}://{parsed.netloc}" in development_frontend_origins()))
            if (not parsed.hostname or parsed.username or parsed.password
                    or parsed.query or parsed.fragment or parsed.path != path
                    or not (secure or development_origin)
                    or (environment == "production" and local)):
                raise DonationConfigurationError("Invalid donation return URL.")
        if urlsplit(success).netloc != urlsplit(cancel).netloc or urlsplit(success).scheme != urlsplit(cancel).scheme:
            raise DonationConfigurationError("Donation return URLs must share an origin.")
        return cls(environment, key, price, success, cancel)
