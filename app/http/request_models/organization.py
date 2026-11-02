from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from core.enum.organization import OrganizationRole


class OrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class InvitationRequest(BaseModel):
    email: EmailStr
    role: Literal[OrganizationRole.MEMBER, OrganizationRole.ADMIN] = OrganizationRole.MEMBER


class RoleRequest(BaseModel):
    role: Literal[OrganizationRole.MEMBER, OrganizationRole.ADMIN]


class OwnerRequest(BaseModel):
    user_id: int = Field(description="The member who becomes the owner")


class MonthlyLimitRequest(BaseModel):
    monthly_limit: int | None = Field(
        ge=0, description="Kopecks per calendar month from the organization's balance; null: none"
    )
