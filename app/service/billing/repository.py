from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.billing import (
    BillingAccountModel,
    BillingHoldModel,
    BillingPayerModel,
    BillingTransactionModel,
)
from core.db.models.organization import OrganizationMemberModel
from core.db.models.user import UserModel
from core.domain.billing import AccountOwner
from core.enum.billing import BillingOperation, HoldStatus


class BillingRepository:
    """Billing queries. Balance changes go through ``locked_account`` first."""

    def __init__(self, session: AsyncSession):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def locked_account(self, owner: AccountOwner) -> BillingAccountModel:
        """The owner's account, created on first use, locked until the transaction ends."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def locked_account_by_id(self, account_id: int) -> BillingAccountModel:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def account(self, owner: AccountOwner) -> BillingAccountModel | None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def payer_organization(self, user_id: int) -> int | None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def set_payer_organization(self, user_id: int, organization_id: int | None) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def reserved(self, account_id: int) -> int:
        """Money held by holds that can still be charged."""
        # sum() of bigint is numeric in Postgres: Decimal here
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def member_limit(self, organization_id: int, user_id: int) -> int | None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def member_used_this_month(self, account_id: int, user_id: int) -> int:
        """What the member spent from the account this calendar month plus their open holds."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def add_hold(
        self, account_id: int, user_id: int, job_id: int, amount: int, lifetime: timedelta
    ) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def locked_hold(self, job_id: int) -> BillingHoldModel | None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def close_hold(self, hold: BillingHoldModel, status: HoldStatus) -> None:
        await self.session.execute(
            update(BillingHoldModel)
            .where(BillingHoldModel.id == hold.id)
            .values(status=status, settled_at=func.now())
        )

    async def add_entry(
        self,
        account: BillingAccountModel,
        operation: BillingOperation,
        amount: int,
        *,
        job_id: int | None = None,
        user_id: int | None = None,
        external_id: str | None = None,
        comment: str | None = None,
        created_by: int | None = None,
    ) -> None:
        """Append a ledger entry and move the balance by ``amount`` (account locked)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def has_entry(self, external_id: str) -> bool:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def entries(
        self, account_id: int, limit: int, offset: int
    ) -> Sequence[BillingTransactionModel]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def is_admin(self, user_id: int) -> bool:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


def _owned_by(owner: AccountOwner):
    raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")
