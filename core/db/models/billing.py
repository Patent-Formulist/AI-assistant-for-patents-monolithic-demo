from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.sql import func

from core.db.db import Base
from core.enum.billing import BillingOperation, HoldStatus


class BillingAccountModel(Base):
    """Money of a user or of an organization (exactly one). Amounts are in kopecks.

    ``balance`` is the sum of the account's ledger entries, kept here so a
    hold can check it under one row lock.
    """

    __tablename__ = "billing_accounts"
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(user_id, organization_id) = 1", name="ck_billing_accounts_one_owner"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, unique=True
    )
    organization_id = Column(
        BigInteger,
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
        unique=True,
    )
    balance = Column(BigInteger, nullable=False, default=0, comment="Копейки")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class BillingTransactionModel(Base):
    """Append-only ledger: every change of a balance. ``amount`` is signed."""

    __tablename__ = "billing_transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(
        BigInteger,
        ForeignKey("billing_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    operation = Column(PGEnum(BillingOperation, name="billing_operation"), nullable=False)
    amount = Column(BigInteger, nullable=False, comment="Копейки, со знаком")
    job_id = Column(BigInteger, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    # Who spent or paid: on an organization's account, which member
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # Payment provider id or another key that makes a repeated request a no-op
    external_id = Column(String(100), nullable=True, unique=True)
    comment = Column(String(500), nullable=True)
    created_by = Column(BigInteger, nullable=True, comment="Администратор для корректировок")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class BillingHoldModel(Base):
    """Money reserved for a running pipeline: charged when it completes, released if not.

    A hold past ``expires_at`` no longer reserves anything: its workflow can no
    longer finish (Temporal ended it on the execution timeout or by hand).
    """

    __tablename__ = "billing_holds"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_billing_holds_amount_positive"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(
        BigInteger,
        ForeignKey("billing_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        BigInteger, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    # The member who started the pipeline
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    amount = Column(BigInteger, nullable=False, comment="Копейки")
    status = Column(PGEnum(HoldStatus, name="hold_status"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    settled_at = Column(DateTime, nullable=True)


class BillingPayerModel(Base):
    """A user pays for pipelines from this organization's account; no row: their own."""

    __tablename__ = "billing_payers"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
