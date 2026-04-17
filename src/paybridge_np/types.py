"""Type aliases for PayBridgeNP SDK.

These are TypedDicts that mirror the TypeScript SDK types. They are used
for type checking only -- the SDK accepts and returns plain dicts at runtime.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

# ── Common ───────────────────────────────────────────────────────────────────

Provider = Literal["esewa", "khalti", "connectips", "hamropay", "imepay"]
PaymentStatus = Literal["pending", "processing", "success", "failed", "cancelled", "refunded"]
Metadata = dict[str, Any]

# ── Checkout ─────────────────────────────────────────────────────────────────


class CustomerInfo(TypedDict, total=False):
    name: str
    email: str
    phone: str


class CreateCheckoutParams(TypedDict, total=False):
    amount: int  # Required -- in paisa (NPR x 100)
    provider: Provider
    returnUrl: str  # Required
    cancelUrl: str
    currency: str
    metadata: Metadata
    customer: CustomerInfo


class CheckoutSession(TypedDict):
    id: str
    checkout_url: str
    expires_at: str


# ── Payments ─────────────────────────────────────────────────────────────────


class Payment(TypedDict):
    id: str
    project_id: str
    checkout_session_id: str | None
    amount: int
    currency: str
    provider: Provider
    provider_ref: str | None
    status: PaymentStatus
    metadata: Metadata | None
    created_at: str
    updated_at: str


class PaginationMeta(TypedDict):
    total: int
    limit: int
    offset: int


# ── Refunds ──────────────────────────────────────────────────────────────────

RefundStatus = Literal["processing", "succeeded", "failed", "requires_action"]
RefundReason = Literal["customer_request", "duplicate", "fraudulent", "other"]


class CreateRefundParams(TypedDict, total=False):
    paymentId: str  # Required
    amount: int  # Required
    reason: RefundReason  # Required
    notes: str
    mobileNumber: str


# ── Webhooks ─────────────────────────────────────────────────────────────────

WebhookEventType = Literal["payment.succeeded", "payment.failed", "payment.cancelled"]


class CreateWebhookParams(TypedDict, total=False):
    url: str  # Required
    events: list[WebhookEventType]


class UpdateWebhookParams(TypedDict, total=False):
    url: str
    events: list[WebhookEventType]
    enabled: bool


# ── Plans ────────────────────────────────────────────────────────────────────

IntervalUnit = Literal["day", "week", "month", "quarter", "year"]
OverdueAction = Literal["keep_active", "mark_past_due", "pause", "cancel"]


class CreatePlanParams(TypedDict, total=False):
    name: str  # Required
    amount: int  # Required
    intervalUnit: IntervalUnit  # Required
    intervalCount: int
    currency: str
    description: str | None
    gracePeriodDays: int
    trialDays: int
    defaultProvider: Provider | None
    reminderDaysBeforeDue: int
    overdueReminderIntervalDays: int
    overdueAction: OverdueAction
    metadata: Metadata | None


class UpdatePlanParams(TypedDict, total=False):
    name: str
    description: str | None
    active: bool
    defaultProvider: Provider | None
    gracePeriodDays: int
    reminderDaysBeforeDue: int
    overdueReminderIntervalDays: int
    overdueAction: OverdueAction


# ── Customers ────────────────────────────────────────────────────────────────


class CreateCustomerParams(TypedDict, total=False):
    name: str  # Required
    email: str | None
    phone: str | None
    externalCustomerId: str | None
    metadata: Metadata | None


class UpdateCustomerParams(TypedDict, total=False):
    name: str
    email: str | None
    phone: str | None
    externalCustomerId: str | None
    metadata: Metadata | None


# ── Subscriptions ────────────────────────────────────────────────────────────

SubscriptionStatus = Literal["active", "past_due", "paused", "cancelled", "completed"]


class CreateSubscriptionParams(TypedDict, total=False):
    customerId: str  # Required
    planId: str  # Required
    referenceId: str
    startDate: str
    metadata: Metadata | None


class PauseSubscriptionParams(TypedDict, total=False):
    pauseReason: str
    resumeAt: str


class CancelSubscriptionParams(TypedDict, total=False):
    cancelReason: str
    atPeriodEnd: bool


class ChangePlanParams(TypedDict, total=False):
    newPlanId: str  # Required
    effectiveAt: str


# ── Invoices ─────────────────────────────────────────────────────────────────

InvoiceStatus = Literal["draft", "open", "paid", "overdue", "void", "uncollectible"]
