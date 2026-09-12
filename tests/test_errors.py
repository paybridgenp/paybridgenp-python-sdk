"""Tests for error creation.

The v1 envelope is nested: ``type`` names the class, ``code`` is a separate,
optional machine string. These tests were written against the 0.x contract
(``code`` holding the type, ``raw`` passed positionally where ``code`` now
lives) and sat red in the repo until 2026-09-12.
"""

from paybridge_np.errors import (
    PayBridgeError,
    ApiError,
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    create_error,
    parse_error_response,
)


def test_create_error_401():
    err = create_error("Unauthorized", 401, {"error": "Unauthorized"})
    assert isinstance(err, AuthenticationError)
    assert err.status_code == 401
    assert err.type == "authentication_error"
    # No `code` in a legacy flat body — the type is not a code.
    assert err.code is None


def test_create_error_400():
    err = create_error("Bad request", 400, None)
    assert isinstance(err, InvalidRequestError)


def test_create_error_422():
    err = create_error("Unprocessable", 422, None)
    assert isinstance(err, InvalidRequestError)


def test_create_error_404():
    err = create_error("Not found", 404, None)
    assert isinstance(err, NotFoundError)
    # And still catchable as the parent, which is what new code should use.
    assert isinstance(err, InvalidRequestError)
    assert err.status_code == 404


def test_nested_envelope_404_is_also_not_found():
    err = parse_error_response(404, {"error": {"message": "No such payment", "type": "invalid_request_error", "code": "resource_missing"}})
    assert isinstance(err, NotFoundError)
    assert err.code == "resource_missing"
    assert str(err) == "No such payment"


def test_create_error_429():
    err = create_error("Rate limited", 429, None)
    assert isinstance(err, RateLimitError)


def test_rate_limit_carries_retry_after():
    err = parse_error_response(429, {"error": {"message": "slow down", "type": "rate_limit_error"}}, "30")
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 30


def test_create_error_500():
    err = create_error("Server error", 500, None)
    assert isinstance(err, PayBridgeError)
    assert isinstance(err, ApiError)
    assert err.type == "api_error"


def test_error_to_dict():
    err = AuthenticationError("bad key", raw={"detail": "invalid"})
    d = err.to_dict()
    assert d["name"] == "AuthenticationError"
    assert d["type"] == "authentication_error"
    assert d["code"] is None
    assert d["status_code"] == 401
    assert d["raw"]["detail"] == "invalid"


def test_explicit_type_wins_over_status():
    """A 404 typed permission_error is a PermissionError, not a NotFoundError."""
    from paybridge_np.errors import PermissionError as PbPermissionError

    err = parse_error_response(404, {"error": {"message": "no", "type": "permission_error"}})
    assert isinstance(err, PbPermissionError)
    assert not isinstance(err, NotFoundError)


def test_unknown_type_falls_back_to_status():
    err = parse_error_response(404, {"error": {"message": "no", "type": "brand_new_error"}})
    assert isinstance(err, NotFoundError)


def test_metadata_survives_parsing():
    body = {"error": {"message": "no", "type": "invalid_request_error", "code": "resource_missing", "request_id": "req_1"}}
    err = parse_error_response(404, body)
    assert err.request_id == "req_1"
    assert err.raw is body
    assert err.to_dict()["name"] == "NotFoundError"
