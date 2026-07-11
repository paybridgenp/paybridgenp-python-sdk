"""Official Python SDK for the PayBridgeNP payment gateway."""

from .client import PayBridgeNP
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

SDK_VERSION = "3.2.1"

__all__ = [
    "PayBridgeNP",
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
