"""Official Python SDK for the PayBridgeNP payment gateway."""

from .client import PayBridge
from .errors import (
    PayBridgeError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    ConnectionError as PayBridgeConnectionError,
    SignatureVerificationError,
)

SDK_VERSION = "0.4.0"

__all__ = [
    "PayBridge",
    "PayBridgeError",
    "AuthenticationError",
    "InvalidRequestError",
    "NotFoundError",
    "RateLimitError",
    "PayBridgeConnectionError",
    "SignatureVerificationError",
    "SDK_VERSION",
]
