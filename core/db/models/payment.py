from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.sql import func

from core.db.db import Base
from core.enum.billing import PaymentStatus, RefundStatus


class PaymentModel(Base):
    """A top-up through a payment provider. The balance changes only on success."""

    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # Paid into the organization's account; NULL: the user's own
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=True
    )
    provider = Column(String(30), nullable=False)
    provider_payment_id = Column(String(100), nullable=False, unique=True)
    amount = Column(BigInteger, nullable=False, comment="Копейки")
    status = Column(PGEnum(PaymentStatus, name="payment_status"), nullable=False)
    confirmation_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RefundModel(Base):
    """Money of a succeeded payment returned through the provider.

    The balance is debited before the provider is asked; ``idempotence_key``
    makes asking again (after a network failure) return the same refund.
    """

    __tablename__ = "refunds"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    payment_id = Column(
        BigInteger, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    amount = Column(BigInteger, nullable=False, comment="Копейки")
    status = Column(PGEnum(RefundStatus, name="refund_status"), nullable=False)
    idempotence_key = Column(String(64), nullable=False, unique=True)
    provider_refund_id = Column(String(100), nullable=True, unique=True)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
