"""PayBridgeNP SDK error types."""

from __future__ import annotations

from typing import Any


class PayBridgeError(Exception):
    """Base error for all PayBridgeNP API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        code: str = "api_error",
        raw: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.raw = raw

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": type(self).__name__,
            "message": str(self),
            "code": self.code,
            "status_code": self.status_code,
            "raw": self.raw,
        }


class AuthenticationError(PayBridgeError):
    def __init__(self, message: str, raw: dict[str, Any] | None = None) -> None:
        super().__init__(message, 401, "authentication_error", raw)


class InvalidRequestError(PayBridgeError):
    def __init__(self, message: str, raw: dict[str, Any] | None = None) -> None:
        super().__init__(message, 400, "invalid_request_error", raw)


class NotFoundError(PayBridgeError):
    def __init__(self, message: str, raw: dict[str, Any] | None = None) -> None:
        super().__init__(message, 404, "not_found_error", raw)


class RateLimitError(PayBridgeError):
    def __init__(self, message: str, raw: dict[str, Any] | None = None) -> None:
        super().__init__(message, 429, "rate_limit_error", raw)


class ConnectionError(PayBridgeError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Connection error: {message}", 0, "connection_error")


class SignatureVerificationError(PayBridgeError):
    def __init__(self, message: str = "Webhook signature verification failed") -> None:
        super().__init__(message, 0, "signature_verification_error")


def create_error(
    message: str, status_code: int, raw: dict[str, Any] | None
) -> PayBridgeError:
    if status_code == 401:
        return AuthenticationError(message, raw)
    if status_code == 404:
        return NotFoundError(message, raw)
    if status_code in (400, 422):
        return InvalidRequestError(message, raw)
    if status_code == 429:
        return RateLimitError(message, raw)
    return PayBridgeError(message, status_code, "api_error", raw)
