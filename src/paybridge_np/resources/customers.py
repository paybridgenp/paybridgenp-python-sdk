"""Billing customers resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateCustomerParams, UpdateCustomerParams


class CustomersResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateCustomerParams) -> dict[str, Any]:
        """Create a customer."""
        return self._http.post("/v1/billing/customers", json=params)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """List customers."""
        qs_parts: dict[str, str] = {}
        if page is not None:
            qs_parts["page"] = str(page)
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if search is not None:
            qs_parts["search"] = search
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/billing/customers{'?' + qs if qs else ''}")

    def get(self, customer_id: str) -> dict[str, Any]:
        """Retrieve a customer by ID."""
        return self._http.get(f"/v1/billing/customers/{customer_id}")

    def update(self, customer_id: str, params: UpdateCustomerParams) -> dict[str, Any]:
        """Update a customer."""
        return self._http.patch(f"/v1/billing/customers/{customer_id}", json=params)

    def delete(self, customer_id: str) -> dict[str, Any]:
        """Delete a customer. Returns ``{"deleted": true}``."""
        return self._http.delete(f"/v1/billing/customers/{customer_id}")

    def add_credit(self, customer_id: str, amount: int, note: str | None = None) -> dict[str, Any]:
        """Add credits to a customer's balance (use negative amount to deduct).

        Credits are applied automatically against future invoices before payment.
        ``amount`` is in paisa (NPR × 100).
        """
        body: dict[str, Any] = {"amount": amount}
        if note is not None:
            body["note"] = note
        return self._http.post(f"/v1/billing/customers/{customer_id}/credit", json=body)
