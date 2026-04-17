"""Refunds resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateRefundParams


class RefundsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateRefundParams) -> dict[str, Any]:
        """Create a refund.

        Args:
            params: Must include ``payment_id``, ``amount``, and ``reason``.
        """
        return self._http.post("/v1/refunds", json=params)

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
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/refunds{'?' + qs if qs else ''}")

    def retrieve(self, refund_id: str) -> dict[str, Any]:
        """Retrieve a single refund by ID."""
        return self._http.get(f"/v1/refunds/{refund_id}")
