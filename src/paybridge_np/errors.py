"""PayBridgeNP SDK error types (v1.0+).

Mirrors the API's nested error envelope::

    {"error": {"message": ..., "type": ..., "code": ..., "request_id": ..., ...}}

The ``type`` field drives the class hierarchy below — branch with ``isinstance``
rather than comparing strings.
"""

from __future__ import annotations

from typing import Any


class PayBridgeError(Exception):
    """Base error for all PayBridgeNP API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        type_: str = "api_error",
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        # ``type`` shadows a builtin if we use it as a parameter name, so the
        # ctor takes ``type_`` and stores it as the public ``type`` attribute.
        self.type = type_
        self.code = code
        self.request_id = request_id
        self.raw = raw

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": type(self).__name__,
            "message": str(self),
            "type": self.type,
            "code": self.code,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "raw": self.raw,
        }


class AuthenticationError(PayBridgeError):
    def __init__(
        self,
        message: str,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 401, "authentication_error", code, request_id, raw)


class AccountError(PayBridgeError):
    """Credentials valid, but the account/token is not in good standing.

    Two common cases (check ``self.code``):

    - ``account_suspended`` (403): merchant account suspended; ``self.suspension``
      holds ``{"suspended_at": ..., "reason": ...}``.
    - ``token_paused`` (423): MCP token paused; ``self.pause`` holds
      ``{"paused_at": ..., "reason": ...}``.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 403,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, "account_error", code, request_id, raw)

    @property
    def suspension(self) -> dict[str, Any] | None:
        if not self.raw or not isinstance(self.raw.get("error"), dict):
            return None
        return self.raw["error"].get("suspension")

    @property
    def pause(self) -> dict[str, Any] | None:
        if not self.raw or not isinstance(self.raw.get("error"), dict):
            return None
        return self.raw["error"].get("pause")


class PermissionError(PayBridgeError):  # noqa: A001 (shadows builtin intentionally)
    def __init__(
        self,
        message: str,
        status_code: int = 403,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, "permission_error", code, request_id, raw)


class InvalidRequestError(PayBridgeError):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, "invalid_request_error", code, request_id, raw)


class NotFoundError(InvalidRequestError):
    """Pre-1.0 alias. 404 is now an ``InvalidRequestError`` (Stripe convention).

    Kept as a subclass so ``except NotFoundError`` keeps working. Prefer
    ``except InvalidRequestError`` and check ``e.status_code == 404``.
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 404, code, request_id, raw)


class IdempotencyError(PayBridgeError):
    def __init__(
        self,
        message: str,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 409, "idempotency_error", code, request_id, raw)


class RateLimitError(PayBridgeError):
    """Public-API rate-limit window exhausted. Back off for ``self.retry_after`` seconds."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, 429, "rate_limit_error", code, request_id, raw)
        self.retry_after = retry_after


class ApiError(PayBridgeError):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str | None = None,
        request_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, "api_error", code, request_id, raw)


class ConnectionError(PayBridgeError):  # noqa: A001
    def __init__(self, message: str) -> None:
        super().__init__(f"Connection error: {message}", 0, "connection_error")


class SignatureVerificationError(PayBridgeError):
    def __init__(self, message: str = "Webhook signature verification failed") -> None:
        super().__init__(message, 0, "signature_verification_error")


def parse_error_response(
    status_code: int,
    body: dict[str, Any] | None,
    retry_after_header: str | None = None,
) -> PayBridgeError:
    """Build the matching typed error from an error response body.

    Accepts the v1+ nested envelope; tolerates the legacy flat shape so
    pre-3.0 API responses keep working during migration.
    """
    err_obj = body.get("error") if isinstance(body, dict) else None

    if isinstance(err_obj, dict):
        message = err_obj.get("message") or f"HTTP {status_code}"
        type_ = err_obj.get("type")
        code = err_obj.get("code")
        request_id = err_obj.get("request_id")
    else:
        # Legacy flat shape.
        message = body.get("error") if isinstance(body, dict) and isinstance(body.get("error"), str) else f"HTTP {status_code}"
        type_ = None
        code = body.get("code") if isinstance(body, dict) else None
        request_id = None

    if type_ == "authentication_error":
        return AuthenticationError(message, code, request_id, body)
    if type_ == "account_error":
        return AccountError(message, status_code, code, request_id, body)
    if type_ == "permission_error":
        return PermissionError(message, status_code, code, request_id, body)
    if type_ == "invalid_request_error":
        return InvalidRequestError(message, status_code, code, request_id, body)
    if type_ == "idempotency_error":
        return IdempotencyError(message, code, request_id, body)
    if type_ == "rate_limit_error":
        retry_after = int(retry_after_header) if retry_after_header else None
        return RateLimitError(message, code, request_id, body, retry_after)
    if type_ == "api_error":
        return ApiError(message, status_code, code, request_id, body)

    # No type field — derive from status (legacy flat shape).
    if status_code == 401:
        return AuthenticationError(message, code, request_id, body)
    if status_code == 403:
        return PermissionError(message, status_code, code, request_id, body)
    if 400 <= status_code < 500:
        if status_code == 429:
            retry_after = int(retry_after_header) if retry_after_header else None
            return RateLimitError(message, code, request_id, body, retry_after)
        return InvalidRequestError(message, status_code, code, request_id, body)
    return ApiError(message, status_code, code, request_id, body)


def create_error(
    message: str, status_code: int, raw: dict[str, Any] | None
) -> PayBridgeError:
    """Deprecated. Use ``parse_error_response`` instead."""
    return parse_error_response(status_code, raw, None)
