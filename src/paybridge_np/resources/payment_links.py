"""Payment links resource.

Reusable hosted payment pages. Mirrors the public ``/v1/payment-links`` routes
(all require an API key with the ``links:read`` / ``links:write`` scope).

Note: payment-link responses use camelCase keys (``customerName``,
``expiresAt``, ...), matching the live API.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ..http import HttpClient


class PaymentLinksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a payment link.

        Provide either a fixed ``amount`` (paisa), or ``minAmount``/``maxAmount``
        bounds for a customer-entered amount. Returns the created link
        (HTTP 201).
        """
        return self._http.post("/v1/payment-links", json=params)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        active: bool | None = None,
    ) -> dict[str, Any]:
        """List payment links for the project, newest first. Filter with ``active``.

        Returns:
            dict ``{"data": [...], "meta": {"total", "limit", "offset"}}``.
        """
        qs_parts: dict[str, str] = {}
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if offset is not None:
            qs_parts["offset"] = str(offset)
        if active is not None:
            # API expects the literal strings "true"/"false".
            qs_parts["active"] = "true" if active else "false"
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/payment-links{'?' + qs if qs else ''}")

    def retrieve(self, id: str) -> dict[str, Any]:
        """Retrieve a single link by ID, including aggregated view/conversion stats."""
        return self._http.get(f"/v1/payment-links/{quote(id, safe='')}")

    def update(self, id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Update a link's editable fields. Only the keys you pass are changed."""
        return self._http.patch(f"/v1/payment-links/{quote(id, safe='')}", json=params)

    def cancel(self, id: str) -> dict[str, Any]:
        """Cancel (deactivate) a link so it can no longer accept payments, while
        keeping it and its history for your records. The recommended way to
        retire a link that has already been used."""
        return self._http.post(f"/v1/payment-links/{quote(id, safe='')}/cancel", json={})

    def delete(self, id: str) -> dict[str, Any]:
        """Permanently delete a link. Only allowed when the link has never been
        used -- otherwise the API returns 422 and you should :meth:`cancel` it
        instead.

        Returns:
            dict ``{"deleted": True, "id": ...}``.
        """
        return self._http.delete(f"/v1/payment-links/{quote(id, safe='')}")
