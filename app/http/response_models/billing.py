from datetime import datetime

from pydantic import BaseModel, Field

from core.domain.billing import Balance, LedgerEntry, MemberLimit, Payment, Refund
from core.enum.billing import BillingOperation, PaymentStatus, RefundStatus


class BalanceResponse(BaseModel):
    """Amounts in kopecks."""

    balance: int
    reserved: int = Field(description="Held by running pipelines")
    available: int = Field(description="What a new operation may use")
    currency: str = "RUB"

    @classmethod
    def of(cls, balance: Balance) -> "BalanceResponse":
        return cls(balance=balance.balance, reserved=balance.reserved, available=balance.available)


class LedgerEntryResponse(BaseModel):
    id: int
    operation: BillingOperation
    amount: int = Field(description="Kopecks: positive adds, negative takes")
    created_at: datetime
    job_id: int | None = None
    comment: str | None = None
    user_id: int | None = Field(default=None, description="Who spent or paid")

    @classmethod
    def of(cls, entry: LedgerEntry) -> "LedgerEntryResponse":
        return cls(
            id=entry.id,
            operation=entry.operation,
            amount=entry.amount,
            created_at=entry.created_at,
            job_id=entry.job_id,
            comment=entry.comment,
            user_id=entry.user_id,
        )


class PayerResponse(BaseModel):
    """Whose balance pays for the user's pipelines; organization_id null: their own."""

    organization_id: int | None


class PricesResponse(BaseModel):
    """Full price of each pipeline in kopecks, by job type."""

    prices: dict[str, int]
    currency: str = "RUB"


class PaymentResponse(BaseModel):
    id: int
    amount: int = Field(description="Kopecks")
    status: PaymentStatus
    confirmation_url: str | None = Field(description="Payment page to send the user to")
    created_at: datetime
    organization_id: int | None = None

    @classmethod
    def of(cls, payment: Payment) -> "PaymentResponse":
        return cls(
            id=payment.id,
            amount=payment.amount,
            status=payment.status,
            confirmation_url=payment.confirmation_url,
            created_at=payment.created_at,
            organization_id=payment.organization_id,
        )


class MemberLimitResponse(BaseModel):
    """Kopecks; monthly_limit and remaining null: no limit."""

    monthly_limit: int | None
    used: int = Field(description="Charged this calendar month plus running pipelines")
    remaining: int | None

    @classmethod
    def of(cls, limit: MemberLimit) -> "MemberLimitResponse":
        return cls(monthly_limit=limit.monthly_limit, used=limit.used, remaining=limit.remaining)


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: int = Field(description="Kopecks")
    status: RefundStatus
    created_at: datetime

    @classmethod
    def of(cls, refund: Refund) -> "RefundResponse":
        return cls(
            id=refund.id,
            payment_id=refund.payment_id,
            amount=refund.amount,
            status=refund.status,
            created_at=refund.created_at,
        )
