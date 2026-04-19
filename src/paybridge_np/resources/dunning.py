"""Dunning resource (Phase 3)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient


class DunningResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    # ── Policies ──────────────────────────────────────────────────────────────

    def create_policy(
        self,
        *,
        name: str,
        retry_intervals_days: list[int],
        final_action: str = "cancel",
        is_default: bool = False,
    ) -> dict[str, Any]:
        """Create a dunning policy."""
        return self._http.post(
            "/v1/billing/dunning/policies",
            json={
                "name": name,
                "retryIntervalsDays": retry_intervals_days,
                "finalAction": final_action,
                "isDefault": is_default,
            },
        )

    def list_policies(self) -> dict[str, Any]:
        """List all dunning policies. Returns ``{"data": [...]}"``."""
        return self._http.get("/v1/billing/dunning/policies")

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        """Retrieve a single dunning policy."""
        return self._http.get(f"/v1/billing/dunning/policies/{policy_id}")

    def update_policy(self, policy_id: str, **params: Any) -> dict[str, Any]:
        """Update a dunning policy. Accepts name, retryIntervalsDays, finalAction, isDefault, active."""
        return self._http.patch(f"/v1/billing/dunning/policies/{policy_id}", json=params)

    # ── Subscription policy assignment ────────────────────────────────────────

    def set_subscription_policy(
        self, subscription_id: str, policy_id: str | None
    ) -> dict[str, Any]:
        """Assign a dunning policy to a subscription. Pass policy_id=None to revert to merchant default."""
        return self._http.post(
            f"/v1/billing/dunning/subscriptions/{subscription_id}/policy",
            json={"policyId": policy_id},
        )

    # ── Invoice dunning actions ────────────────────────────────────────────────

    def get_invoice_status(self, invoice_id: str) -> dict[str, Any]:
        """Get the current dunning state for an invoice, including attempt history."""
        return self._http.get(f"/v1/billing/dunning/invoices/{invoice_id}/dunning")

    def stop_invoice(self, invoice_id: str) -> dict[str, Any]:
        """Stop the dunning cycle for an invoice. No further reminders will be sent."""
        return self._http.post(
            f"/v1/billing/dunning/invoices/{invoice_id}/dunning/stop", json={}
        )

    def retry_invoice_now(self, invoice_id: str) -> dict[str, Any]:
        """Immediately trigger the next dunning retry for an invoice."""
        return self._http.post(
            f"/v1/billing/dunning/invoices/{invoice_id}/dunning/retry-now", json={}
        )
