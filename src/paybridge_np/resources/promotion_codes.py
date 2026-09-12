"""Promotion codes resource (Phase 2)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import (
        CreatePromotionCodeParams,
        ValidatePromotionCodeParams,
    )


class PromotionCodesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        params: CreatePromotionCodeParams,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Create a customer-facing promotion code that redeems a coupon.

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.post(
            "/v1/billing/promotion-codes", json=params,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        coupon_id: str | None = None,
        active: bool | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """List promotion codes."""
        qs_parts: dict[str, str] = {}
        if coupon_id:
            qs_parts["couponId"] = coupon_id
        if active is not None:
            qs_parts["active"] = str(active).lower()
        if limit is not None:
            qs_parts["limit"] = str(limit)
        return self._http.get("/v1/billing/promotion-codes", params=qs_parts or None)

    def get(self, promotion_code_id: str) -> dict[str, Any]:
        """Retrieve a promotion code by ID."""
        return self._http.get(f"/v1/billing/promotion-codes/{promotion_code_id}")

    def deactivate(
        self,
        promotion_code_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Deactivate a promotion code. Existing redemptions remain valid.

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.patch(
            f"/v1/billing/promotion-codes/{promotion_code_id}", json={"active": False},
            idempotency_key=idempotency_key,
        )

    def validate(
        self,
        params: ValidatePromotionCodeParams,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Validate a code and preview the discount. Read-only — does NOT redeem.

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.post(
            "/v1/billing/promotion-codes/validate", json=params,
            idempotency_key=idempotency_key,
        )
