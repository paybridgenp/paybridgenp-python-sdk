"""Billing invoices resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

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
