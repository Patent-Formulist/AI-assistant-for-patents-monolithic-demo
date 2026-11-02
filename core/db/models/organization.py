from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.sql import func

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin
from core.enum.organization import InvitationStatus, OrganizationRole


class OrganizationModel(Base, SoftDeleteMixin):
    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrganizationMemberModel(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_members_user"),
        # One owner per organization
        Index(
            "uq_organization_members_owner",
            "organization_id",
            unique=True,
            postgresql_where=text("role = 'OWNER'"),
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(PGEnum(OrganizationRole, name="organization_role"), nullable=False)
    # Kopecks the member may spend from the organization's balance per calendar
    # month; NULL: no limit
    monthly_limit = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class OrganizationInvitationModel(Base):
    """An invitation by email: the invited user joins only by accepting it."""

    __tablename__ = "organization_invitations"
    __table_args__ = (
        # One open invitation per email in an organization
        Index(
            "uq_organization_invitations_pending",
            "organization_id",
            "email",
            unique=True,
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(String(255), nullable=False, index=True)
    role = Column(PGEnum(OrganizationRole, name="organization_role"), nullable=False)
    status = Column(PGEnum(InvitationStatus, name="invitation_status"), nullable=False)
    invited_by = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    answered_at = Column(DateTime, nullable=True)
