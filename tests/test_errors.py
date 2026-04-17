"""Tests for error creation."""

from paybridge_np.errors import (
    PayBridgeError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    create_error,
)


def test_create_error_401():
    err = create_error("Unauthorized", 401, {"error": "Unauthorized"})
    assert isinstance(err, AuthenticationError)
    assert err.status_code == 401
    assert err.code == "authentication_error"


def test_create_error_400():
    err = create_error("Bad request", 400, None)
    assert isinstance(err, InvalidRequestError)


def test_create_error_422():
    err = create_error("Unprocessable", 422, None)
    assert isinstance(err, InvalidRequestError)


def test_create_error_404():
    err = create_error("Not found", 404, None)
    assert isinstance(err, NotFoundError)


def test_create_error_429():
    err = create_error("Rate limited", 429, None)
    assert isinstance(err, RateLimitError)


def test_create_error_500():
    err = create_error("Server error", 500, None)
    assert isinstance(err, PayBridgeError)
    assert err.code == "api_error"


def test_error_to_dict():
    err = AuthenticationError("bad key", {"detail": "invalid"})
    d = err.to_dict()
    assert d["name"] == "AuthenticationError"
    assert d["code"] == "authentication_error"
    assert d["status_code"] == 401
    assert d["raw"]["detail"] == "invalid"
