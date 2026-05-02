# paybridge-np

Official Python SDK for the [PayBridgeNP](https://paybridgenp.com) payment gateway. Accept eSewa, Khalti, and ConnectIPS through a single API.

## Installation

```bash
pip install paybridge-np
```

## Quick start

```python
from paybridge_np import PayBridge

client = PayBridge(api_key="sk_live_...")  # from dashboard.paybridgenp.com

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
```

## Payments

```python
# List payments
result = client.payments.list(limit=20)
payments = result["data"]

# Get a single payment
payment = client.payments.retrieve("pay_xxx")
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
    signature=request.headers["X-PayBridge-Signature"],
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

Use a sandbox API key (`sk_sandbox_...`) to test without real money. The SDK automatically routes to sandbox endpoints.

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

## Context manager

```python
with PayBridge(api_key="sk_live_...") as client:
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
