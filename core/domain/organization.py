from dataclasses import dataclass
from datetime import datetime

from core.enum.organization import InvitationStatus, OrganizationRole


@dataclass(frozen=True)
class Organization:
    id: int
    name: str
    # Role of the user who asked
    role: OrganizationRole
    created_at: datetime


@dataclass(frozen=True)
class Member:
    user_id: int
    email: str | None
    role: OrganizationRole
    joined_at: datetime
    # Kopecks per calendar month from the organization's balance; None: no limit
    monthly_limit: int | None = None


@dataclass(frozen=True)
class Invitation:
    id: int
    organization_id: int
    organization_name: str
    email: str
    role: OrganizationRole
    status: InvitationStatus
    created_at: datetime
