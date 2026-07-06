"""Billing invoices resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..http import HttpClient


class InvoicesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        customer_id: str | None = None,
        subscription_id: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """List invoices."""
        qs_parts: dict[str, str] = {}
        if page is not None:
            qs_parts["page"] = str(page)
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if status is not None:
            qs_parts["status"] = status
        if customer_id is not None:
            qs_parts["customerId"] = customer_id
        if subscription_id is not None:
            qs_parts["subscriptionId"] = subscription_id
        if search is not None:
            qs_parts["search"] = search
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/billing/invoices{'?' + qs if qs else ''}")

    def get(self, invoice_id: str) -> dict[str, Any]:
        """Retrieve an invoice by ID."""
        return self._http.get(f"/v1/billing/invoices/{invoice_id}")

    def qr(self, invoice_id: str) -> dict[str, Any]:
        """Mint a Fonepay Direct-QR to pay this invoice.

        The customer scans it (in your own UI / at a counter) and on success the
        invoice is marked paid and the subscription activates
        (``incomplete``->``active``) -- the same outcome as the hosted bill page,
        just collected via an embedded QR. Returns a normal Direct-QR session
        (use its ``events_url`` SSE stream + ``qr.refresh(id)``). Hits
        ``POST /v1/billing/invoices/{id}/qr``.

        Premium feature; requires the ``billing:write`` scope and Fonepay configured.

        Returns:
            dict with id, invoice_id, amount, currency, provider, status,
            qr_message, qr_image (data URL), events_url, expires_at.
        """
        return self._http.post(f"/v1/billing/invoices/{quote(invoice_id, safe='')}/qr", json={})
