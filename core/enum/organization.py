import enum


class OrganizationRole(str, enum.Enum):
    """OWNER: everything, one per organization; ADMIN: members and money; MEMBER: works."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"
