"""Direct-QR API for Fonepay (Premium feature)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient


class QrResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def fonepay(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a Fonepay Direct-QR session.

        Returns the raw EMV QR string, a base64-encoded PNG image, and a
        per-session SSE URL the customer's browser can subscribe to for
        real-time payment events (qr.scanned, qr.paid, qr.expired).

        Premium feature -- the merchant must be on the Premium plan, or
        this call returns 403 with ``entitlement: "fonepay.directQr"``.

        Args:
            params: dict with keys:
                - amount (int, paisa)
                - currency (optional, defaults to "NPR")
                - customer (dict with name, email, optional phone, optional address)
                - metadata (optional dict)

        Returns:
            dict with id, qr_message, qr_image (data URL), events_url, expires_at.
        """
        return self._http.post("/v1/qr/fonepay", json=params)
