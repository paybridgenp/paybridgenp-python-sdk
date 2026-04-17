"""Tests for webhook signature verification."""

import hashlib
import hmac
import json
import time

import pytest

from paybridge_np.errors import SignatureVerificationError
from paybridge_np.resources.webhooks import WebhooksResource


def _sign(body: str, secret: str, timestamp: int | None = None) -> str:
    ts = timestamp or int(time.time())
    sig = hmac.new(
        secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256
    ).hexdigest()
    return f"t={ts},v1={sig}"


SECRET = "whsec_test_secret"
EVENT = {"id": "evt_1", "type": "payment.succeeded", "created": 1700000000, "data": {"amount": 100}}
BODY = json.dumps(EVENT)


def test_valid_signature():
    sig = _sign(BODY, SECRET)
    result = WebhooksResource.construct_event(BODY, sig, SECRET)
    assert result["id"] == "evt_1"
    assert result["type"] == "payment.succeeded"


def test_missing_signature():
    with pytest.raises(SignatureVerificationError, match="Missing"):
        WebhooksResource.construct_event(BODY, None, SECRET)


def test_empty_signature():
    with pytest.raises(SignatureVerificationError, match="Missing"):
        WebhooksResource.construct_event(BODY, "", SECRET)


def test_malformed_signature():
    with pytest.raises(SignatureVerificationError, match="Malformed"):
        WebhooksResource.construct_event(BODY, "garbage", SECRET)


def test_wrong_secret():
    sig = _sign(BODY, "wrong_secret")
    with pytest.raises(SignatureVerificationError):
        WebhooksResource.construct_event(BODY, sig, SECRET)


def test_expired_timestamp():
    old_ts = int(time.time()) - 600  # 10 minutes ago
    sig = _sign(BODY, SECRET, old_ts)
    with pytest.raises(SignatureVerificationError, match="Timestamp too old"):
        WebhooksResource.construct_event(BODY, sig, SECRET)


def test_tampered_body():
    sig = _sign(BODY, SECRET)
    tampered = BODY.replace("100", "999")
    with pytest.raises(SignatureVerificationError):
        WebhooksResource.construct_event(tampered, sig, SECRET)
