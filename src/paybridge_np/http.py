"""HTTP client with retries and exponential backoff."""

from __future__ import annotations

import random
import time
from typing import Any

import httpx

from .errors import ConnectionError, parse_error_response

DEFAULT_BASE_URL = "https://api.paybridgenp.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
RETRY_STATUSES = {500, 502, 503, 504}
INITIAL_BACKOFF_S = 0.5


def _backoff(attempt: int) -> float:
    return INITIAL_BACKOFF_S * (2 ** (attempt - 1)) + random.random() * 0.1


class HttpClient:
    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._api_key = api_key
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "PayBridgeNP-Python/1.0.0",
            },
        )

    def request(self, method: str, path: str, json: Any = None) -> Any:
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._client.request(method, path, json=json)
            except httpx.HTTPError as exc:
                if attempt > self._max_retries:
                    raise ConnectionError(str(exc)) from exc
                time.sleep(_backoff(attempt))
                continue

            if resp.is_success:
                return resp.json()

            if resp.status_code in RETRY_STATUSES and attempt <= self._max_retries:
                retry_after = resp.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else _backoff(attempt)
                time.sleep(delay)
                continue

            raw: dict[str, Any] | None = None
            try:
                raw = resp.json()
            except Exception:
                # Body wasn't JSON. Will surface as `HTTP <status>` with no detail.
                pass

            raise parse_error_response(
                resp.status_code, raw, resp.headers.get("Retry-After")
            )

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, json: Any) -> Any:
        return self.request("POST", path, json=json)

    def patch(self, path: str, json: Any) -> Any:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)

    def close(self) -> None:
        self._client.close()
