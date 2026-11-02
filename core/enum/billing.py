import enum


class BillingOperation(str, enum.Enum):
    """Ledger entry kinds: what changed the balance."""

    TOP_UP = "top_up"
    CHARGE = "charge"
    ADJUSTMENT = "adjustment"
    # Money paid back through the provider (negative), or put back if it refused
    REFUND = "refund"


class HoldStatus(str, enum.Enum):
    HELD = "held"
    CHARGED = "charged"
    RELEASED = "released"


class PaymentStatus(str, enum.Enum):
    """Statuses of a YooKassa payment."""

    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class RefundStatus(str, enum.Enum):
    """CREATED: debited, not yet accepted by the provider (a retry is safe)."""

    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
