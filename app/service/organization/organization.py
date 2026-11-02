from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.billing import BillingAccountModel
from core.db.models.organization import (
    OrganizationInvitationModel,
    OrganizationMemberModel,
    OrganizationModel,
)
from core.db.models.user import UserModel
from core.domain.organization import Invitation, Member, Organization
from core.enum.organization import InvitationStatus, OrganizationRole
from core.exceptions import (
    AccessDeniedError,
    EmailNotVerifiedError,
    OrganizationConflictError,
    OrganizationNotFoundError,
)

OWNER, ADMIN, MEMBER = OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.MEMBER
MANAGERS = (OWNER, ADMIN)


class OrganizationService:
    """Organizations of users: membership, roles and invitations.

    Access rules live here (coding-standards: no checks in routes):
    - an organization is visible only to its members; to others it does not exist (404);
    - the owner does everything; there is exactly one, the creator;
    - admins invite and remove members; only the owner grants or invites admins;
    - users join only by accepting an invitation sent to their email, and only
      with that email confirmed: otherwise whoever registered someone else's
      address first would see and take their invitations.
    Runs in the request session: the caller commits.
    """

    def __init__(self, session: AsyncSession):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Organizations ----------

    async def create(self, user_id: int, name: str) -> Organization:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def for_user(self, user_id: int) -> list[Organization]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def get(self, user_id: int, organization_id: int) -> Organization:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def rename(self, user_id: int, organization_id: int, name: str) -> Organization:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def delete(self, user_id: int, organization_id: int) -> None:
        """Soft delete: membership and history stay, the organization disappears.

        Refused while its balance is not zero: the money would be stranded.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Members ----------

    async def members(self, user_id: int, organization_id: int) -> list[Member]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def change_role(
        self, user_id: int, organization_id: int, member_id: int, role: OrganizationRole
    ) -> Member:
        """Owner only; ownership is not transferred this way."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def transfer_ownership(
        self, user_id: int, organization_id: int, new_owner_id: int
    ) -> list[Member]:
        """The owner hands the organization to a member and stays as an admin."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def set_monthly_limit(
        self, user_id: int, organization_id: int, member_id: int, limit: int | None
    ) -> Member:
        """Limit a member's spending from the organization's balance per month (None: none).

        The owner limits anyone but themselves; admins limit members only.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def remove(self, user_id: int, organization_id: int, member_id: int) -> None:
        """Remove a member, or leave when ``member_id`` is the user."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Invitations ----------

    async def invite(
        self, user_id: int, organization_id: int, email: str, role: OrganizationRole
    ) -> Invitation:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def organization_invitations(
        self, user_id: int, organization_id: int
    ) -> list[Invitation]:
        """Pending invitations of the organization (owner and admins)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def revoke(self, user_id: int, organization_id: int, invitation_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def my_invitations(self, user_id: int) -> list[Invitation]:
        """Pending invitations to the user's confirmed email in organizations that still exist."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def answer(self, user_id: int, invitation_id: int, accept: bool) -> Organization | None:
        """Accept (join with the invited role) or decline an invitation to the user's email."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Helpers ----------

    async def role(self, user_id: int, organization_id: int) -> OrganizationRole:
        """The user's role; OrganizationNotFoundError for non-members (for other services)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _role(self, user_id: int, organization_id: int) -> OrganizationRole:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _require(
        self, user_id: int, organization_id: int, roles: tuple[OrganizationRole, ...]
    ) -> OrganizationRole:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _member(self, organization_id: int, user_id: int) -> OrganizationMemberModel:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _pending(self, invitation_id: int) -> OrganizationInvitationModel:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _confirmed_email(self, user_id: int) -> str:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _invitation(self, invitation: OrganizationInvitationModel) -> Invitation:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _organization(model: OrganizationModel, role: OrganizationRole) -> Organization:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")
