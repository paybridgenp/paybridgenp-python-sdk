"""Webhooks resource with signature verification."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
from typing import Any, TYPE_CHECKING

from ..errors import SignatureVerificationError

if TYPE_CHECKING:
    from ..http import HttpClient


class WebhooksResource:
    def __init__(self, http: HttpClient | None = None) -> None:
        self._http = http

    def _require_http(self) -> HttpClient:
        if self._http is None:
            raise RuntimeError("WebhooksResource requires an HttpClient")
        return self._http

    def create(
        self,
        *,
        url: str,
        events: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register a webhook endpoint. Returns the endpoint with ``signing_secret``."""
        body: dict[str, Any] = {"url": url}
        if events is not None:
            body["events"] = events
        return self._require_http().post("/v1/webhooks", json=body)

    def list(self) -> dict[str, Any]:
        """List all webhook endpoints."""
        return self._require_http().get("/v1/webhooks")

    def update(
        self,
        endpoint_id: str,
        *,
        url: str | None = None,
        events: list[str] | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        """Update a webhook endpoint."""
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if enabled is not None:
            body["enabled"] = enabled
        return self._require_http().patch(f"/v1/webhooks/{endpoint_id}", json=body)

    def delete(self, endpoint_id: str) -> dict[str, Any]:
        """Delete a webhook endpoint."""
        return self._require_http().delete(f"/v1/webhooks/{endpoint_id}")

    def list_deliveries(self, endpoint_id: str) -> dict[str, Any]:
        """List deliveries for a webhook endpoint."""
        return self._require_http().get(f"/v1/webhooks/{endpoint_id}/deliveries")

    @staticmethod
    def construct_event(
        body: str,
        signature: str | None,
        secret: str,
    ) -> dict[str, Any]:
        """Verify a webhook signature and parse the event.

        Args:
            body: Raw request body string (do NOT parse as JSON first).
            signature: Value of the ``X-PayBridge-Signature`` header.
            secret: Your webhook signing secret (``whsec_...``).

        Returns:
            Parsed webhook event dict.

        Raises:
            SignatureVerificationError: If the signature is missing, malformed, or invalid.
        """
        if not signature:
            raise SignatureVerificationError("Missing X-PayBridge-Signature header")

        parts: dict[str, str] = {}
        for part in signature.split(","):
            key, _, value = part.partition("=")
            parts[key] = value

        timestamp = parts.get("t")
        v1 = parts.get("v1")

        if not timestamp or not v1:
            raise SignatureVerificationError("Malformed signature header")

        # Replay attack protection: reject if timestamp is >5 minutes old
        ts = int(timestamp)
        now = int(time.time())
        if abs(now - ts) > 300:
            raise SignatureVerificationError(
                "Timestamp too old - possible replay attack"
            )

        # Compute expected HMAC
        expected = hmac.new(
            secret.encode(),
            f"{timestamp}.{body}".encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(v1, expected):
            raise SignatureVerificationError()

        return json.loads(body)
