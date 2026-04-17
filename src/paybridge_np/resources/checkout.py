"""Checkout sessions."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateCheckoutParams, CheckoutSession


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
