# paybridge-np

Official Python SDK for the [PayBridgeNP](https://paybridgenp.com) payment gateway. Accept eSewa, Khalti, and Fonepay through a single API.

## Installation

```bash
pip install paybridge-np
```

## Quick start

```python
from paybridge_np import PayBridgeNP

client = PayBridgeNP(api_key="sk_live_...")  # from dashboard.paybridgenp.com

# Create a checkout session
session = client.checkout.create({
    "amount": 250000,        # NPR 2,500 in paisa
    "currency": "NPR",
    "returnUrl": "https://mystore.com/success",
    "cancelUrl": "https://mystore.com/cart",
    "metadata": {"orderId": "ORD-7842"},
    "customer": {
        "name": "Ram Shrestha",
        "email": "ram@example.com",
        "phone": "9841000000",
    },
})

# Redirect customer to hosted checkout
# session["checkout_url"] => https://checkout.paybridgenp.com/checkout/cs_xxx

# Expire a previously-created session so its URL stops being payable
# (use when you mint a fresh session for the same purchase).
client.checkout.expire("cs_xxx")

# Retrieve or list checkout sessions (read-only). The read shape uses
# camelCase keys (customerName, expiresAt, ...).
session = client.checkout.retrieve("cs_xxx")
sessions = client.checkout.list(limit=20, status="success")
```

## Payments

```python
# List payments
result = client.payments.list(limit=20)
payments = result["data"]

# Get a single payment
payment = client.payments.retrieve("pay_xxx")
```

## Payment links

Reusable hosted payment pages. Responses use camelCase keys.

```python
# Create
link = client.payment_links.create({"title": "Donation", "amount": 50000})

# List, retrieve (with view/conversion stats), update, cancel, or delete
links = client.payment_links.list(active=True)
detail = client.payment_links.retrieve(link["id"])
client.payment_links.update(link["id"], {"active": False})
client.payment_links.cancel(link["id"])  # deactivate, keep for records
client.payment_links.delete(link["id"])  # only if never used
```

## Direct-QR (Fonepay)

Premium feature -- mint a Fonepay QR server-side and embed it in your own UI,
skipping the hosted checkout page. Subscribe to ``events_url`` (SSE) for
``qr.scanned`` / ``qr.paid`` / ``qr.expired``.

```python
qr = client.qr.fonepay({
    "amount": 10000,  # paisa
    "customer": {"name": "Aarav Sharma", "email": "aarav@example.com"},
})
# qr["qr_image"] (PNG data URL), qr["qr_message"], qr["events_url"], qr["expires_at"]

# The QR display window is ~3 min. Refresh it for the SAME session -- same id,
# events_url, and webhook -- without spawning a new session. Lifetime unchanged.
fresh = client.qr.refresh(qr["id"])
```

## Refunds

```python
refund = client.refunds.create({
    "paymentId": "pay_xxx",
    "amount": 100000,  # NPR 1,000 in paisa
    "reason": "customer_request",
})
```

## Webhooks

```python
# Register an endpoint
endpoint = client.webhooks.create(
    url="https://mystore.com/webhooks/paybridge",
    events=["payment.succeeded", "payment.failed"],
)

# Verify a webhook signature (no client instance needed)
from paybridge_np.resources.webhooks import WebhooksResource

event = WebhooksResource.construct_event(
    body=raw_body,
    signature=request.headers["X-PayBridgeNP-Signature"],
    secret="whsec_...",
)
```

## Billing (Subscriptions)

```python
# Create a plan
plan = client.plans.create({
    "name": "Pro Monthly",
    "amount": 99900,
    "intervalUnit": "month",
})

# Create a customer
customer = client.customers.create({
    "name": "Sita Gurung",
    "email": "sita@example.com",
})

# Subscribe
subscription = client.subscriptions.create({
    "customerId": customer["id"],
    "planId": plan["id"],
})

# List invoices
invoices = client.invoices.list(customer_id=customer["id"])
```

## Sandbox mode

Use a test-mode API key (`sk_test_...`) to test without real money. Mode is determined server-side by the key prefix (`sk_test_` vs `sk_live_`) - there is nothing to configure in the SDK.

## Retries and idempotency (3.3.0)

Only GET requests are automatically retried after connection errors or HTTP
500/502/503/504 responses, up to `max_retries` times (default: 2). Set
`max_retries=0` to disable retries. POST, PATCH, and DELETE requests are sent once,
even when a caller supplies an idempotency key.

Every POST, PATCH, and DELETE sends an `Idempotency-Key` header. By default it is
a fresh UUID for each method call. All resource methods using these verbs accept
an optional keyword-only `idempotency_key`:

```python
refund = client.refunds.create(
    {"paymentId": "pay_123", "amount": 10000, "reason": "customer_request"},
    idempotency_key="refund-order-123",
)
```

Persist a key per business operation and reuse it with the same request when
retrying manually. A new method call without a supplied key generates a new UUID;
it does not reuse the previous call's key. Replay protection is endpoint-specific:
sending a key does not guarantee deduplication on every route. If a write fails
with an unknown outcome, check its status before retrying.

## Error handling

```python
from paybridge_np import PayBridgeError, AuthenticationError

try:
    session = client.checkout.create({...})
except AuthenticationError:
    print("Invalid API key")
except PayBridgeError as e:
    print(e, e.status_code)
```

Errors carry a `type` (which names the class) and an optional `code` (a machine
string from the API, often `None`). A 404 raises `NotFoundError`, which subclasses
`InvalidRequestError` — catch either.

## Context manager

```python
with PayBridgeNP(api_key="sk_live_...") as client:
    session = client.checkout.create({...})
# HTTP client is closed automatically
```

## Documentation

- [API Reference](https://docs.paybridgenp.com)
- [Dashboard](https://dashboard.paybridgenp.com)
- [Guides](https://docs.paybridgenp.com/guides/sandbox-testing)
- [Discord](https://discord.gg/aquta4JwJt)

## License

MIT
