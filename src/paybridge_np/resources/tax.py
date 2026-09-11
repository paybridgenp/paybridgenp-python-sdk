"""Tax settings resource (Phase 2)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import UpdateTaxSettingsParams


class TaxResource:
    """Account-level tax configuration applied to invoices."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_settings(self) -> dict[str, Any]:
        """Get the current tax settings."""
        return self._http.get("/v1/billing/settings/tax")

    def update_settings(
        self,
        params: "UpdateTaxSettingsParams",
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update tax settings (enabled, rateBps, registrationNumber, label).

        ``idempotency_key`` sets the request header; omitted keys default to a new UUID.
        Replay protection depends on the endpoint; writes are never auto-retried.
        """
        return self._http.patch("/v1/billing/settings/tax", json=params, idempotency_key=idempotency_key)
