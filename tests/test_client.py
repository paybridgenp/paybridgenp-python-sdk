"""Tests for client initialization and resource access."""

from paybridge_np import PayBridge
from paybridge_np.resources.checkout import CheckoutResource
from paybridge_np.resources.payments import PaymentsResource
from paybridge_np.resources.refunds import RefundsResource
from paybridge_np.resources.webhooks import WebhooksResource
from paybridge_np.resources.plans import PlansResource
from paybridge_np.resources.customers import CustomersResource
from paybridge_np.resources.subscriptions import SubscriptionsResource
from paybridge_np.resources.invoices import InvoicesResource


def test_client_resources():
    client = PayBridge(api_key="sk_test_xxx")
    assert isinstance(client.checkout, CheckoutResource)
    assert isinstance(client.payments, PaymentsResource)
    assert isinstance(client.refunds, RefundsResource)
    assert isinstance(client.webhooks, WebhooksResource)
    assert isinstance(client.plans, PlansResource)
    assert isinstance(client.customers, CustomersResource)
    assert isinstance(client.subscriptions, SubscriptionsResource)
    assert isinstance(client.invoices, InvoicesResource)
    client.close()


def test_lazy_initialization():
    client = PayBridge(api_key="sk_test_xxx")
    # Access twice, should return the same instance
    checkout1 = client.checkout
    checkout2 = client.checkout
    assert checkout1 is checkout2
    client.close()


def test_context_manager():
    with PayBridge(api_key="sk_test_xxx") as client:
        assert isinstance(client.checkout, CheckoutResource)


def test_static_webhook_utility():
    assert isinstance(PayBridge.webhooks_static, WebhooksResource)
