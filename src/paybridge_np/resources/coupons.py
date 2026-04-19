"""Coupons resource (Phase 2)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreateCouponParams


class CouponsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateCouponParams) -> dict[str, Any]:
        """Create a reusable discount coupon.

        Discount params (type, percent/amount off) are immutable post-creation.
        To change terms, deactivate and create a new coupon.
        """
        return self._http.post("/v1/billing/coupons", json=params)

    def list(
        self,
        *,
        active: bool | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """List coupons. Returns ``{"data": [...]}``."""
        qs_parts: dict[str, str] = {}
        if active is not None:
            qs_parts["active"] = str(active).lower()
        if limit is not None:
            qs_parts["limit"] = str(limit)
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/billing/coupons{'?' + qs if qs else ''}")

    def get(self, coupon_id: str) -> dict[str, Any]:
        """Retrieve a coupon by ID."""
        return self._http.get(f"/v1/billing/coupons/{coupon_id}")

    def deactivate(self, coupon_id: str) -> dict[str, Any]:
        """Deactivate a coupon (soft-delete)."""
        return self._http.delete(f"/v1/billing/coupons/{coupon_id}")
