"""Billing plans resource."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http import HttpClient
    from ..types import CreatePlanParams, UpdatePlanParams


class PlansResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, params: CreatePlanParams) -> dict[str, Any]:
        """Create a billing plan."""
        return self._http.post("/v1/billing/plans", json=params)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        active: bool | None = None,
    ) -> dict[str, Any]:
        """List plans. Returns ``{"data": [...], "total", "page", "limit"}``."""
        qs_parts: dict[str, str] = {}
        if page is not None:
            qs_parts["page"] = str(page)
        if limit is not None:
            qs_parts["limit"] = str(limit)
        if active is not None:
            qs_parts["active"] = str(active).lower()
        qs = "&".join(f"{k}={v}" for k, v in qs_parts.items())
        return self._http.get(f"/v1/billing/plans{'?' + qs if qs else ''}")

    def get(self, plan_id: str) -> dict[str, Any]:
        """Retrieve a plan by ID."""
        return self._http.get(f"/v1/billing/plans/{plan_id}")

    def update(self, plan_id: str, params: UpdatePlanParams) -> dict[str, Any]:
        """Update a plan."""
        return self._http.patch(f"/v1/billing/plans/{plan_id}", json=params)
