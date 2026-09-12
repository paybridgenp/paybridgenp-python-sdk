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

    def create(
        self,
        params: CreateCheckoutParams,
        *,
        idempotency_key: str | None = None,
    ) -> CheckoutSession:
        """Create a checkout session.

        Args:
            params: Checkout parameters including amount (in paisa), return_url, etc.

        Returns:
            CheckoutSession with ``id`` and ``checkout_url``.

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.post("/v1/checkout", json=params, idempotency_key=idempotency_key)

    def expire(self, id: str, *, idempotency_key: str | None = None) -> ExpiredCheckoutSession:
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

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.post(
            f"/v1/checkout/{quote(id, safe='')}/expire", json={},
            idempotency_key=idempotency_key,
        )

    def retrieve(self, id: str) -> dict[str, Any]:
        """Retrieve a checkout session by ID.

        Read-only -- sessions are created via :meth:`create`. Hits
        ``GET /v1/sessions/{id}``.

        Note: this richer read shape uses camelCase keys (``customerName``,
        ``expiresAt``, ...), unlike the snake_case ``create`` response.

        Args:
            id: The checkout session id (e.g. ``cs_...``).

        Returns:
            dict with the session's status, amount, customer, and any
            collected address.
        """
        return self._http.get(f"/v1/sessions/{quote(id, safe='')}")

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List checkout sessions for the project, newest first.

        Optionally filter by ``status`` and page with ``limit``/``offset``.
        Hits ``GET /v1/sessions``.

        Returns:
            dict ``{"data": [...], "meta": {"total", "limit", "offset"}}``.
        """
        qs_parts: dict[str, str] = {}
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if offset is not None:
            qs_parts["offset"] = str(offset)
        if status is not None:
            qs_parts["status"] = status
        return self._http.get("/v1/sessions", params=qs_parts or None)
