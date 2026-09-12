"""Refunds resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateRefundParams


class RefundsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        params: CreateRefundParams,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a refund.

        Args:
            params: Must include ``payment_id``, ``amount``, and ``reason``.

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.post("/v1/refunds", json=params, idempotency_key=idempotency_key)

    def list(
        self,
        *,
        payment_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List refunds, optionally filtered by payment ID."""
        qs_parts: dict[str, str] = {}
        if payment_id is not None:
            qs_parts["paymentId"] = payment_id
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if offset is not None:
            qs_parts["offset"] = str(offset)
        return self._http.get("/v1/refunds", params=qs_parts or None)

    def retrieve(self, refund_id: str) -> dict[str, Any]:
        """Retrieve a single refund by ID."""
        return self._http.get(f"/v1/refunds/{refund_id}")
