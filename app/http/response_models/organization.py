from dataclasses import asdict
from datetime import datetime

from pydantic import BaseModel

from core.domain.organization import Invitation, Member, Organization
from core.enum.organization import InvitationStatus, OrganizationRole


class OrganizationResponse(BaseModel):
    id: int
    name: str
    role: OrganizationRole
    created_at: datetime

    @classmethod
    def of(cls, organization: Organization) -> "OrganizationResponse":
        return cls(**asdict(organization))


class MemberResponse(BaseModel):
    user_id: int
    email: str | None
    role: OrganizationRole
    joined_at: datetime
    monthly_limit: int | None = None

    @classmethod
    def of(cls, member: Member) -> "MemberResponse":
        return cls(**asdict(member))


class InvitationResponse(BaseModel):
    id: int
    organization_id: int
    organization_name: str
    email: str
    role: OrganizationRole
    status: InvitationStatus
    created_at: datetime

    @classmethod
    def of(cls, invitation: Invitation) -> "InvitationResponse":
        return cls(**asdict(invitation))
