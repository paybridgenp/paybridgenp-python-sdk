"""Checkout sessions."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateCheckoutParams, CheckoutSession, ExpiredCheckoutSession


class CheckoutResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateCheckoutParams) -> CheckoutSession:
        """Create a checkout session.

        Args:
            params: Checkout parameters including amount (in paisa), return_url, etc.

        Returns:
            CheckoutSession with ``id`` and ``checkout_url``.
        """
        return self._http.post("/v1/checkout", json=params)

    def expire(self, id: str) -> ExpiredCheckoutSession:
        """Expire a checkout session so it can no longer accept payment.

        Use this when you mint a fresh checkout session for a logical
        purchase that already had one outstanding (a customer requesting a
        new payment link, your reminder system regenerating expired URLs,
        etc.). Without an explicit expire call, the old URL stays payable
        until its 30-minute TTL elapses, which can let a customer who
        reloads the old tab pay twice. Mirrors Stripe's
        ``POST /checkout/sessions/{id}/expire``.

        Idempotent: calling on an already-terminal session is a no-op that
        returns the current row state without error.

        Args:
            id: The checkout session id (e.g. ``cs_...``).

        Returns:
            ExpiredCheckoutSession with ``status`` reflecting the current state.
        """
        return self._http.post(f"/v1/checkout/{quote(id, safe='')}/expire", json={})
