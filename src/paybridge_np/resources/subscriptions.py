"""Billing subscriptions resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import (
        ApplyCouponParams,
        CreateSubscriptionParams,
        PauseSubscriptionParams,
        CancelSubscriptionParams,
        ChangePlanParams,
        ExtendTrialParams,
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
        """Change the plan on a subscription.

        Pass ``prorationBehavior="create_prorations"`` to apply immediately and
        generate a proration invoice for the net difference. Default (``"none"``)
        schedules the change for the next billing cycle.
        """
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/change-plan",
            json=params,
        )

    def preview_proration(
        self, subscription_id: str, new_plan_id: str
    ) -> dict[str, Any]:
        """Preview the proration credit/debit for a mid-period plan change.

        Returns ``{ creditAmount, debitAmount, netAmount, currency, periodStart,
        periodEnd, currentPlan, newPlan }`` without committing any changes.
        """
        from urllib.parse import urlencode
        qs = urlencode({"newPlanId": new_plan_id})
        return self._http.get(
            f"/v1/billing/subscriptions/{subscription_id}/preview-proration?{qs}"
        )

    def end_trial(self, subscription_id: str) -> dict[str, Any]:
        """End a subscription's trial immediately.

        Generates the first paid invoice and emails it to the customer.
        Fires ``subscription.trial_ended`` webhook. Returns
        ``{ "subscription": {...}, "invoice": {...} }``.
        """
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/end-trial", json={}
        )

    def extend_trial(
        self, subscription_id: str, params: ExtendTrialParams
    ) -> dict[str, Any]:
        """Push a subscription's trial end into the future.

        Only valid while the trial is still active. Re-arms the 3-day-before
        reminder. Fires ``subscription.trial_extended`` webhook.
        """
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/extend-trial",
            json=params,
        )

    def apply_coupon(
        self, subscription_id: str, params: ApplyCouponParams
    ) -> dict[str, Any]:
        """Attach a coupon or promotion code to a subscription.

        Takes effect on the next invoice. Deactivates any prior active
        discount on this sub. Pass either ``couponId`` or ``promotionCode``.
        """
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/apply-coupon",
            json=params,
        )

    def remove_discount(self, subscription_id: str) -> dict[str, Any]:
        """Remove the currently active discount. Future invoices un-discounted."""
        return self._http.delete(
            f"/v1/billing/subscriptions/{subscription_id}/discount"
        )

    # ── Usage (metered billing) ───────────────────────────────────────────────

    def report_usage(self, subscription_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Report a usage event. action='increment' (default) or 'set'. Pass idempotency_key to prevent double-counting."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/usage",
            json=params,
        )

    def get_usage_summary(self, subscription_id: str) -> dict[str, Any]:
        """Get aggregated usage for the current billing period."""
        return self._http.get(
            f"/v1/billing/subscriptions/{subscription_id}/usage"
        )

    def list_usage_records(self, subscription_id: str, limit: int = 50) -> dict[str, Any]:
        """List raw usage records for a subscription."""
        return self._http.get(
            f"/v1/billing/subscriptions/{subscription_id}/usage/records",
            params={"limit": limit},
        )

    # ── Pending Invoice Items ─────────────────────────────────────────────────

    def list_invoice_items(self, subscription_id: str) -> list[dict[str, Any]]:
        """List pending one-off charges that will be included in the next invoice."""
        return self._http.get(
            f"/v1/billing/subscriptions/{subscription_id}/invoice-items"
        )

    def create_invoice_item(self, subscription_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Add a one-off charge consumed on the next invoice."""
        return self._http.post(
            f"/v1/billing/subscriptions/{subscription_id}/invoice-items",
            json=params,
        )

    def delete_invoice_item(self, subscription_id: str, item_id: str) -> dict[str, Any]:
        """Delete a pending invoice item before it is invoiced."""
        return self._http.delete(
            f"/v1/billing/subscriptions/{subscription_id}/invoice-items/{item_id}"
        )

    def update_quantity(self, subscription_id: str, quantity: int) -> dict[str, Any]:
        """Update the per-seat quantity on an active per_unit subscription."""
        return self._http.patch(
            f"/v1/billing/subscriptions/{subscription_id}/quantity",
            json={"quantity": quantity},
        )
