"""Billing subscriptions resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import (
        CreateSubscriptionParams,
        PauseSubscriptionParams,
        CancelSubscriptionParams,
        ChangePlanParams,
    )


class SubscriptionsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreateSubscriptionParams) -> dict[str, Any]:
        """Create a subscription."""
        return self._http.post("/v1/billing/subscriptions", json=params)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        customer_id: str | None = None,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        """List subscriptions."""
        qs_parts: dict[str, str] = {}
        if page is not None:
            qs_parts["page"] = str(page)
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if status is not None:
            qs_parts["status"] = status
        if customer_id is not None:
            qs_parts["customerId"] = customer_id
        if plan_id is not None:
            qs_parts["planId"] = plan_id
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/billing/subscriptions{'?' + qs if qs else ''}")

    def get(self, subscription_id: str) -> dict[str, Any]:
        """Retrieve a subscription by ID."""
        return self._http.get(f"/v1/billing/subscriptions/{subscription_id}")

    def pause(
        self, subscription_id: str, params: PauseSubscriptionParams | None = None
    ) -> dict[str, Any]:
        """Pause a subscription."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/pause",
            json=params or {},
        )

    def resume(self, subscription_id: str) -> dict[str, Any]:
        """Resume a paused subscription."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/resume", json={}
        )

    def cancel(
        self, subscription_id: str, params: CancelSubscriptionParams | None = None
    ) -> dict[str, Any]:
        """Cancel a subscription."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/cancel",
            json=params or {},
        )

    def change_plan(
        self, subscription_id: str, params: ChangePlanParams
    ) -> dict[str, Any]:
        """Change the plan on a subscription."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/change-plan",
            json=params,
        )
