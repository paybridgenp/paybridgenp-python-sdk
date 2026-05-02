"""Official Python SDK for the PayBridgeNP payment gateway."""

from .client import PayBridge
from .errors import (
    PayBridgeError,
    AuthenticationError,
    AccountError,
    PermissionError,
    InvalidRequestError,
    NotFoundError,  # deprecated alias for InvalidRequestError(404)
    IdempotencyError,
    RateLimitError,
    ApiError,
    ConnectionError as PayBridgeConnectionError,
    SignatureVerificationError,
    parse_error_response,
)

SDK_VERSION = "1.0.0"

__all__ = [
    "PayBridge",
    "PayBridgeError",
    "AuthenticationError",
    "AccountError",
    "PermissionError",
    "InvalidRequestError",
    "NotFoundError",
    "IdempotencyError",
    "RateLimitError",
    "ApiError",
    "PayBridgeConnectionError",
    "SignatureVerificationError",
    "parse_error_response",
    "SDK_VERSION",
]
