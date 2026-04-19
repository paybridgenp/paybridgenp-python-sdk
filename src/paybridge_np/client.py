"""Main PayBridge client."""

from __future__ import annotations

from .http import HttpClient
from .resources.checkout import CheckoutResource
from .resources.payments import PaymentsResource
from .resources.refunds import RefundsResource
from .resources.webhooks import WebhooksResource
from .resources.plans import PlansResource
from .resources.customers import CustomersResource
from .resources.subscriptions import SubscriptionsResource
from .resources.invoices import InvoicesResource
from .resources.coupons import CouponsResource
from .resources.promotion_codes import PromotionCodesResource
from .resources.dunning import DunningResource


class PayBridge:
    """PayBridgeNP API client.

    Usage::

        from paybridge_np import PayBridge

        client = PayBridge(api_key="sk_live_...")
        session = client.checkout.create({
            "amount": 250000,
            "returnUrl": "https://mystore.com/success",
        })
    """

    # Static webhook utility -- no instance required for signature verification.
    webhooks_static = WebhooksResource()

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._checkout: CheckoutResource | None = None
        self._payments: PaymentsResource | None = None
        self._refunds: RefundsResource | None = None
        self._webhooks: WebhooksResource | None = None
        self._plans: PlansResource | None = None
        self._customers: CustomersResource | None = None
        self._subscriptions: SubscriptionsResource | None = None
        self._invoices: InvoicesResource | None = None
        self._coupons: CouponsResource | None = None
        self._promotion_codes: PromotionCodesResource | None = None
        self._dunning: DunningResource | None = None

    @property
    def checkout(self) -> CheckoutResource:
        if self._checkout is None:
            self._checkout = CheckoutResource(self._http)
        return self._checkout

    @property
    def payments(self) -> PaymentsResource:
        if self._payments is None:
            self._payments = PaymentsResource(self._http)
        return self._payments

    @property
    def refunds(self) -> RefundsResource:
        if self._refunds is None:
            self._refunds = RefundsResource(self._http)
        return self._refunds

    @property
    def webhooks(self) -> WebhooksResource:
        if self._webhooks is None:
            self._webhooks = WebhooksResource(self._http)
        return self._webhooks

    @property
    def plans(self) -> PlansResource:
        if self._plans is None:
            self._plans = PlansResource(self._http)
        return self._plans

    @property
    def customers(self) -> CustomersResource:
        if self._customers is None:
            self._customers = CustomersResource(self._http)
        return self._customers

    @property
    def subscriptions(self) -> SubscriptionsResource:
        if self._subscriptions is None:
            self._subscriptions = SubscriptionsResource(self._http)
        return self._subscriptions

    @property
    def invoices(self) -> InvoicesResource:
        if self._invoices is None:
            self._invoices = InvoicesResource(self._http)
        return self._invoices

    @property
    def coupons(self) -> CouponsResource:
        if self._coupons is None:
            self._coupons = CouponsResource(self._http)
        return self._coupons

    @property
    def promotion_codes(self) -> PromotionCodesResource:
        if self._promotion_codes is None:
            self._promotion_codes = PromotionCodesResource(self._http)
        return self._promotion_codes

    @property
    def dunning(self) -> DunningResource:
        if self._dunning is None:
            self._dunning = DunningResource(self._http)
        return self._dunning

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> PayBridge:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
