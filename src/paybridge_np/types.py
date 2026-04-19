"""Type aliases for PayBridgeNP SDK.

These are TypedDicts that mirror the TypeScript SDK types. They are used
for type checking only -- the SDK accepts and returns plain dicts at runtime.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

# ── Common ───────────────────────────────────────────────────────────────────

Provider = Literal["esewa", "khalti", "connectips", "hamropay"]
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
    # Trial override. trialEndsAt (ISO 8601) wins over trialDays (0-365)
    # wins over the plan default. Both omitted = use plan's trialDays.
    trialDays: int
    trialEndsAt: str
    # Per-seat multiplier (default 1, only for per_unit plans).
    quantity: int
    # Pin period-end to this calendar day (1-28) for month/quarter/year intervals.
    billingAnchorDay: int | None
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


class ExtendTrialParams(TypedDict, total=False):
    trialEndsAt: str  # Required, ISO 8601 — must be after current trial end


# ── Coupons + Promotion Codes (Phase 2) ─────────────────────────────────────

CouponDiscountType = Literal["percent", "amount"]
CouponDuration = Literal["once", "repeating", "forever"]


class CreateCouponParams(TypedDict, total=False):
    code: str  # Required
    name: str  # Required
    discountType: CouponDiscountType  # Required
    duration: CouponDuration  # Required
    percentOff: int  # 1..100 when discountType='percent'
    amountOff: int  # paisa when discountType='amount'
    currency: str
    durationInCycles: int  # Required when duration='repeating'
    maxRedemptions: int
    redeemBy: str  # ISO 8601
    appliesToPlanIds: list[str]
    projectIds: list[str]
    metadata: Metadata | None


class CreatePromotionCodeParams(TypedDict, total=False):
    couponId: str  # Required
    code: str  # Required, case-insensitive (auto-uppercased)
    maxRedemptions: int
    expiresAt: str  # ISO 8601
    firstTimeTransaction: bool
    minimumAmount: int  # paisa
    customerIds: list[str]
    metadata: Metadata | None


class ValidatePromotionCodeParams(TypedDict, total=False):
    code: str  # Required
    customerId: str
    planId: str
    amount: int  # paisa, for minimumAmount check


class ApplyCouponParams(TypedDict, total=False):
    couponId: str
    promotionCode: str


# ── Tax (Phase 2) ───────────────────────────────────────────────────────────


class UpdateTaxSettingsParams(TypedDict, total=False):
    enabled: bool
    rateBps: int  # 1300 = 13.00%
    registrationNumber: str | None
    label: str | None


# ── Invoices ─────────────────────────────────────────────────────────────────

InvoiceStatus = Literal["draft", "open", "paid", "overdue", "void", "uncollectible"]
