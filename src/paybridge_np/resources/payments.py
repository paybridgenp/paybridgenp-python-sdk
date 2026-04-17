"""Payments resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient


class PaymentsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, *, limit: int | None = None, offset: int | None = None) -> dict[str, Any]:
        """List payments.

        Returns:
            ``{"data": [...], "meta": {"total", "limit", "offset"}}``
        """
        params: dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return self._http.get(f"/v1/payments{'?' + qs if qs else ''}")

    def retrieve(self, payment_id: str) -> dict[str, Any]:
        """Retrieve a single payment by ID."""
        return self._http.get(f"/v1/payments/{payment_id}")
