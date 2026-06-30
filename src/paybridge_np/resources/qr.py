"""Direct-QR API for Fonepay (Premium feature)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from urllib.parse import quote

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

    def refresh(self, id: str) -> dict[str, Any]:
        """Refresh a Direct-QR session: regenerate a fresh Fonepay QR for the
        SAME session (same ``id``, ``events_url``, and webhook) without
        spawning a new session.

        The Fonepay QR display window is only ~3 minutes, and some wallets
        (eSewa) reject a stale QR, so call this when ``qr.expired`` fires (or
        proactively) to keep a scannable QR on screen. Takes no body -- the
        amount and customer already live on the session. The session's overall
        lifetime is unchanged. Hits ``POST /v1/qr/{id}/refresh``.

        Premium feature -- the merchant must be on the Premium plan.

        Args:
            id: The Direct-QR session id (e.g. ``cs_...``).

        Returns:
            dict with id, qr_message, qr_image (data URL), events_url, expires_at.
        """
        return self._http.post(f"/v1/qr/{quote(id, safe='')}/refresh", json={})
