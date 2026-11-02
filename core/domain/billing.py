from dataclasses import dataclass
from datetime import datetime

from core.enum.billing import BillingOperation, PaymentStatus, RefundStatus


@dataclass(frozen=True)
class AccountOwner:
    """Whose account: a user's own or an organization's (exactly one is set)."""

    user_id: int | None = None
    organization_id: int | None = None

    def __post_init__(self):
        if (self.user_id is None) == (self.organization_id is None):
            raise ValueError("An account belongs to a user or to an organization")

    @property
    def is_organization(self) -> bool:
        return self.organization_id is not None


@dataclass(frozen=True)
class Balance:
    """Amounts in kopecks. ``available`` is what a new operation may reserve."""

    balance: int
    reserved: int

    @property
    def available(self) -> int:
        return self.balance - self.reserved


@dataclass(frozen=True)
class MemberLimit:
    """A member's monthly spending from an organization's balance, kopecks."""

    monthly_limit: int | None
    used: int  # charged this month plus open holds

    @property
    def remaining(self) -> int | None:
        return None if self.monthly_limit is None else max(self.monthly_limit - self.used, 0)


@dataclass(frozen=True)
class LedgerEntry:
    id: int
    operation: BillingOperation
    amount: int
    created_at: datetime
    job_id: int | None = None
    comment: str | None = None
    # Who spent or paid (on an organization's account, which member)
    user_id: int | None = None


@dataclass(frozen=True)
class Payment:
    id: int
    amount: int
    status: PaymentStatus
    confirmation_url: str | None
    created_at: datetime
    organization_id: int | None = None


@dataclass(frozen=True)
class Refund:
    id: int
    payment_id: int
    amount: int
    status: RefundStatus
    created_at: datetime
