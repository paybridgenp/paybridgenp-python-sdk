"""Retry safety and idempotency headers through the public resource methods."""

import json
from uuid import UUID

import httpx
import pytest

from paybridge_np import ApiError, PayBridgeConnectionError, PayBridgeError, PayBridgeNP, SDK_VERSION


@pytest.fixture
def transport(monkeypatch):
    requests = []
    outcomes = []
    sleeps = []

    def handle(_transport, request):
        requests.append(request)
        outcome = outcomes.pop(0) if outcomes else 200
        if outcome == "connection":
            raise httpx.ConnectError("connection dropped", request=request)
        if outcome == "timeout":
            raise httpx.ReadTimeout("response lost", request=request)
        return httpx.Response(outcome, json={}, request=request)

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", handle)
    monkeypatch.setattr("paybridge_np.http.time.sleep", sleeps.append)
    with PayBridgeNP(api_key="sk_test_example", base_url="https://api.example.test", max_retries=2) as client:
        yield client, requests, outcomes, sleeps


@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE", "post"])
@pytest.mark.parametrize("failure", [500, 502, 503, 504, "connection", "timeout"])
@pytest.mark.parametrize("key", [None, "operation-123"])
def test_writes_are_never_retried(transport, method, failure, key):
    client, requests, outcomes, sleeps = transport
    outcomes.append(failure)
    error = PayBridgeConnectionError if isinstance(failure, str) else ApiError
    with pytest.raises(error):
        client._http.request(method, "/v1/checkout", idempotency_key=key)
    assert len(requests) == 1
    assert sleeps == []
    assert requests[0].headers["Idempotency-Key"]


@pytest.mark.parametrize("failure", [500, 502, 503, 504, "connection", "timeout"])
@pytest.mark.parametrize("method", ["GET", "get"])
def test_get_retries_and_sends_no_key(transport, failure, method):
    client, requests, outcomes, sleeps = transport
    outcomes.extend([failure, 200])
    assert client._http.request(method, "/v1/payments", idempotency_key="ignored") == {}
    assert len(requests) == 2
    assert len(sleeps) == 1
    assert all("Idempotency-Key" not in r.headers for r in requests)


@pytest.mark.parametrize("max_retries,attempts", [(0, 1), (2, 3)])
@pytest.mark.parametrize("failure", [500, "connection"])
def test_get_respects_retry_budget(transport, max_retries, attempts, failure):
    client, requests, outcomes, sleeps = transport
    client._http._max_retries = max_retries
    outcomes.extend([failure] * 4)
    with pytest.raises(PayBridgeError):
        client._http.get("/v1/payments")
    assert len(requests) == attempts
    assert len(sleeps) == attempts - 1


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 422, 429])
def test_get_does_not_retry_other_statuses(transport, status):
    client, requests, outcomes, sleeps = transport
    outcomes.append(status)
    with pytest.raises(PayBridgeError):
        client._http.get("/v1/payments")
    assert len(requests) == 1
    assert sleeps == []


def test_get_honors_retry_after(transport, monkeypatch):
    client, requests, _, sleeps = transport

    def handle(_transport, request):
        requests.append(request)
        return httpx.Response(503 if len(requests) == 1 else 200, json={},
                              headers={"Retry-After": "2"}, request=request)

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", handle)
    assert client._http.get("/v1/payments") == {}
    assert sleeps == [2.0]


@pytest.mark.parametrize("method", ["post", "patch", "delete"])
def test_manual_retry_preserves_key_and_generated_keys_are_per_call(transport, method):
    client, requests, outcomes, _ = transport
    call = getattr(client._http, method)
    args = ("/v1/example",) if method == "delete" else ("/v1/example", {})
    outcomes.extend([500, 200])
    with pytest.raises(ApiError):
        call(*args, idempotency_key="operation-123")
    call(*args, idempotency_key="operation-123")
    call(*args)
    call(*args)
    # None alone requests generation: even an empty caller key is preserved.
    call(*args, idempotency_key="")
    client._http.get("/v1/payments")
    keys = [r.headers.get("Idempotency-Key") for r in requests]
    assert keys[:2] == ["operation-123", "operation-123"]
    assert UUID(keys[2]).version == UUID(keys[3]).version == 4
    assert keys[2] != keys[3]
    assert keys[4:] == ["", None]
    assert requests[0].headers["Authorization"] == "Bearer sk_test_example"
    assert requests[0].headers["User-Agent"] == f"PayBridgeNP-Python/{SDK_VERSION}"


# Every public POST/PATCH/DELETE entry point, including actions and **params.
# Explicit routes and bodies catch a forwarded key accidentally becoming JSON.
WRITE_CALLS = [
    ("checkout.create", ({"amount": 100},), {}, "POST", "/v1/checkout", {"amount": 100}),
    ("checkout.expire", ("cs_1",), {}, "POST", "/v1/checkout/cs_1/expire", {}),
    ("refunds.create", ({"paymentId": "pay_1", "amount": 100},), {}, "POST", "/v1/refunds", {"paymentId": "pay_1", "amount": 100}),
    ("customers.create", ({"name": "Example"},), {}, "POST", "/v1/billing/customers", {"name": "Example"}),
    ("customers.update", ("cus_1", {"name": "Example"}), {}, "PATCH", "/v1/billing/customers/cus_1", {"name": "Example"}),
    ("customers.delete", ("cus_1",), {}, "DELETE", "/v1/billing/customers/cus_1", None),
    ("customers.add_credit", ("cus_1", 100, "Adjustment"), {}, "POST", "/v1/billing/customers/cus_1/credit", {"amount": 100, "note": "Adjustment"}),
    ("plans.create", ({"name": "Basic"},), {}, "POST", "/v1/billing/plans", {"name": "Basic"}),
    ("plans.update", ("plan_1", {"active": False}), {}, "PATCH", "/v1/billing/plans/plan_1", {"active": False}),
    ("coupons.create", ({"name": "Sale"},), {}, "POST", "/v1/billing/coupons", {"name": "Sale"}),
    ("coupons.deactivate", ("coupon_1",), {}, "DELETE", "/v1/billing/coupons/coupon_1", None),
    ("promotion_codes.create", ({"code": "SALE"},), {}, "POST", "/v1/billing/promotion-codes", {"code": "SALE"}),
    ("promotion_codes.deactivate", ("promo_1",), {}, "PATCH", "/v1/billing/promotion-codes/promo_1", {"active": False}),
    ("promotion_codes.validate", ({"code": "SALE"},), {}, "POST", "/v1/billing/promotion-codes/validate", {"code": "SALE"}),
    ("invoices.qr", ("inv_1",), {}, "POST", "/v1/billing/invoices/inv_1/qr", {}),
    ("qr.fonepay", ({"amount": 100},), {}, "POST", "/v1/qr/fonepay", {"amount": 100}),
    ("qr.refresh", ("cs_1",), {}, "POST", "/v1/qr/cs_1/refresh", {}),
    ("payment_links.create", ({"amount": 100},), {}, "POST", "/v1/payment-links", {"amount": 100}),
    ("payment_links.update", ("link_1", {"active": False}), {}, "PATCH", "/v1/payment-links/link_1", {"active": False}),
    ("payment_links.cancel", ("link_1",), {}, "POST", "/v1/payment-links/link_1/cancel", {}),
    ("payment_links.delete", ("link_1",), {}, "DELETE", "/v1/payment-links/link_1", None),
    ("tax.update_settings", ({"enabled": True},), {}, "PATCH", "/v1/billing/settings/tax", {"enabled": True}),
    ("webhooks.create", (), {"url": "https://example.test/hook", "events": ["payment.succeeded"]}, "POST", "/v1/webhooks", {"url": "https://example.test/hook", "events": ["payment.succeeded"]}),
    ("webhooks.update", ("wh_1",), {"enabled": False}, "PATCH", "/v1/webhooks/wh_1", {"enabled": False}),
    ("webhooks.delete", ("wh_1",), {}, "DELETE", "/v1/webhooks/wh_1", None),
    ("dunning.create_policy", (), {"name": "Default", "retry_intervals_days": [1, 3]}, "POST", "/v1/billing/dunning/policies", {"name": "Default", "retryIntervalsDays": [1, 3], "finalAction": "cancel", "isDefault": False}),
    ("dunning.update_policy", ("policy_1",), {"name": "Updated", "retryIntervalsDays": [2]}, "PATCH", "/v1/billing/dunning/policies/policy_1", {"name": "Updated", "retryIntervalsDays": [2]}),
    ("dunning.set_subscription_policy", ("sub_1", None), {}, "POST", "/v1/billing/dunning/subscriptions/sub_1/policy", {"policyId": None}),
    ("dunning.stop_invoice", ("inv_1",), {}, "POST", "/v1/billing/dunning/invoices/inv_1/dunning/stop", {}),
    ("dunning.retry_invoice_now", ("inv_1",), {}, "POST", "/v1/billing/dunning/invoices/inv_1/dunning/retry-now", {}),
    ("subscriptions.create", ({"planId": "plan_1"},), {}, "POST", "/v1/billing/subscriptions", {"planId": "plan_1"}),
    ("subscriptions.pause", ("sub_1", {"resumesAt": "2027-01-01"}), {}, "POST", "/v1/billing/subscriptions/sub_1/pause", {"resumesAt": "2027-01-01"}),
    ("subscriptions.resume", ("sub_1",), {}, "POST", "/v1/billing/subscriptions/sub_1/resume", {}),
    ("subscriptions.cancel", ("sub_1", {"cancelAtPeriodEnd": True}), {}, "POST", "/v1/billing/subscriptions/sub_1/cancel", {"cancelAtPeriodEnd": True}),
    ("subscriptions.change_plan", ("sub_1", {"planId": "plan_2"}), {}, "POST", "/v1/billing/subscriptions/sub_1/change-plan", {"planId": "plan_2"}),
    ("subscriptions.end_trial", ("sub_1",), {}, "POST", "/v1/billing/subscriptions/sub_1/end-trial", {}),
    ("subscriptions.extend_trial", ("sub_1", {"trialEnd": "2027-01-01"}), {}, "POST", "/v1/billing/subscriptions/sub_1/extend-trial", {"trialEnd": "2027-01-01"}),
    ("subscriptions.apply_coupon", ("sub_1", {"couponId": "coupon_1"}), {}, "POST", "/v1/billing/subscriptions/sub_1/apply-coupon", {"couponId": "coupon_1"}),
    ("subscriptions.remove_discount", ("sub_1",), {}, "DELETE", "/v1/billing/subscriptions/sub_1/discount", None),
    ("subscriptions.report_usage", ("sub_1", {"quantity": 3}), {}, "POST", "/v1/billing/subscriptions/sub_1/usage", {"quantity": 3}),
    ("subscriptions.create_invoice_item", ("sub_1", {"amount": 100}), {}, "POST", "/v1/billing/subscriptions/sub_1/invoice-items", {"amount": 100}),
    ("subscriptions.delete_invoice_item", ("sub_1", "item_1"), {}, "DELETE", "/v1/billing/subscriptions/sub_1/invoice-items/item_1", None),
    ("subscriptions.update_quantity", ("sub_1", 3), {}, "PATCH", "/v1/billing/subscriptions/sub_1/quantity", {"quantity": 3}),
]


@pytest.mark.parametrize("caller_key", [False, True], ids=["default-key", "caller-key"])
@pytest.mark.parametrize("name,args,kwargs,method,path,body", WRITE_CALLS, ids=[c[0] for c in WRITE_CALLS])
def test_resource_write_on_wire(transport, caller_key, name, args, kwargs, method, path, body):
    client, requests, _, _ = transport
    resource, operation = name.split(".")
    kwargs = dict(kwargs)
    if caller_key:
        kwargs["idempotency_key"] = "operation-123"
    assert getattr(getattr(client, resource), operation)(*args, **kwargs) == {}
    assert len(requests) == 1
    request = requests[0]
    assert (request.method, request.url.path) == (method, path)
    assert (json.loads(request.content) if request.content else None) == body
    key = request.headers["Idempotency-Key"]
    if caller_key:
        assert key == "operation-123"
    else:
        assert UUID(key).version == 4


def test_usage_body_key_is_independent_of_header_key(transport):
    client, requests, _, _ = transport
    body = {"quantity": 3, "idempotency_key": "usage-event-123"}
    client.subscriptions.report_usage("sub_1", body, idempotency_key="request-123")
    assert json.loads(requests[0].content) == body
    assert requests[0].headers["Idempotency-Key"] == "request-123"


@pytest.mark.parametrize("operation", ["pause", "cancel"])
def test_optional_action_body_stays_optional(transport, operation):
    client, requests, _, _ = transport
    getattr(client.subscriptions, operation)("sub_1", idempotency_key="request-123")
    assert json.loads(requests[0].content) == {}
    assert requests[0].headers["Idempotency-Key"] == "request-123"


def test_get_forwards_query_params(monkeypatch):
    """subscriptions.list_usage_records passed params= to get(), which 3.2.x rejected."""
    from paybridge_np.http import HttpClient

    seen = {}

    class FakeResponse:
        is_success = True
        status_code = 200
        headers = {}

        def json(self):
            return {"ok": True}

    client = HttpClient(api_key="sk_test_x", base_url="https://example.test")

    def fake_request(method, path, json=None, headers=None, params=None):
        seen.update({"method": method, "path": path, "params": params})
        return FakeResponse()

    monkeypatch.setattr(client._client, "request", fake_request)
    assert client.get("/v1/things", params={"limit": 5}) == {"ok": True}
    assert seen == {"method": "GET", "path": "/v1/things", "params": {"limit": 5}}


def test_list_filters_are_percent_encoded(transport):
    """Before 2026-09-12 list filters were pasted raw into the URL, so a value
    containing & or # silently became extra parameters or was truncated."""
    client, requests, _outcomes, _sleeps = transport
    client.customers.list(search="A&B + C#D", limit=5)
    url = requests[-1].url
    assert url.params["search"] == "A&B + C#D"
    assert url.params["limit"] == "5"
    assert len(url.params) == 2
    # The raw query must carry the escapes, not the literal separators.
    query = url.query.decode()
    assert "%26" in query and "%23" in query


def test_list_usage_records_sends_its_query(transport):
    """The public caller, not just the HttpClient helper."""
    client, requests, _outcomes, _sleeps = transport
    client.subscriptions.list_usage_records("sub_123", limit=7)
    assert requests[-1].url.params["limit"] == "7"


def test_list_without_filters_sends_no_query(transport):
    client, requests, _outcomes, _sleeps = transport
    client.customers.list()
    assert requests[-1].url.query == b""
