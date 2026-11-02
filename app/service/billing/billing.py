from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.service.billing.pricing import PriceList
from app.service.billing.repository import BillingRepository
from app.service.legal.legal import ConsentCheck
from app.service.organization.organization import MANAGERS, OrganizationService
from core import logger
from core.domain.billing import AccountOwner, Balance, LedgerEntry, MemberLimit
from core.enum.billing import BillingOperation, HoldStatus
from core.enum.job_type import JobType
from core.exceptions import (
    AccessDeniedError,
    InsufficientFundsError,
    OrganizationNotFoundError,
)

logger = logger.get_logger(__name__)


def format_rub(kopecks: int) -> str:
    raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


class BillingService:
    """Balances of users and organizations: a ledger plus holds.

    A pipeline reserves its price when it starts (a hold on its job); the hold is
    charged when the job completes and released when it fails, so users pay only
    for results. A user pays from their own account or, if they chose one, from
    the account of an organization they are a member of (the payer); the ledger
    records which member spent. Every call runs in its own short transaction,
    like job statuses (ADR 0002): billing must not commit or roll back with
    business data. Balance changes lock the account row, so concurrent holds
    cannot overspend. Amounts are in kopecks.

    Organization accounts: any member may pay from it, see its balance and top
    it up; owners and admins see its history.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        prices: PriceList,
        hold_lifetime: timedelta,
        consents: ConsentCheck | None = None,
    ):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def price(self, task_names: Iterable[str]) -> int:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def pipeline_prices(self) -> dict[JobType, int]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Payer ----------

    async def payer(self, user_id: int) -> AccountOwner:
        """Whose account pays for the user's pipelines."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def set_payer(self, user_id: int, organization_id: int | None) -> AccountOwner:
        """Pay from the organization's account (the user must be a member) or, None, own."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Reading ----------

    async def balance(self, user_id: int, organization_id: int | None = None) -> Balance:
        """The user's balance or, as a member, the organization's."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def history(
        self,
        user_id: int,
        organization_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LedgerEntry]:
        """Ledger entries, newest first: the user's, or the organization's for its managers."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Pipelines ----------

    async def hold(self, user_id: int, job_id: int, amount: int) -> None:
        """Reserve ``amount`` for the job on the payer's account; InsufficientFundsError (402).

        A paid operation needs the required legal documents accepted
        (ConsentRequiredError, 403); free ones never reach here.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def settle(self, job_id: int, completed: bool) -> None:
        """Charge the job's hold if it completed, release it otherwise.

        Idempotent: a settled hold or a job without one (a free pipeline) is a no-op.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Money in ----------

    async def top_up(
        self,
        owner: AccountOwner,
        amount: int,
        external_id: str,
        comment: str,
        user_id: int | None = None,
    ) -> bool:
        """Add money paid through ``external_id`` once; False if it was already added."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def debit_refund(self, owner: AccountOwner, amount: int, refund_id: int) -> None:
        """Take money being refunded off the balance; only what is not spent or held."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def reverse_refund(self, owner: AccountOwner, amount: int, refund_id: int) -> None:
        """The provider refused the refund: put the money back (once)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def adjust(
        self, admin_id: int, owner: AccountOwner, amount: int, comment: str
    ) -> Balance:
        """Admin correction: a bonus, a refund or a write-off (``amount`` signed)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def member_limit(self, user_id: int, organization_id: int) -> MemberLimit:
        """The user's monthly limit in the organization and how much of it is used."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Helpers ----------

    @staticmethod
    async def _check_member_limit(
        repo: BillingRepository, owner: AccountOwner, account_id: int, user_id: int, amount: int
    ) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _payer(self, repo: BillingRepository, user_id: int) -> AccountOwner:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    async def _readable(
        repo: BillingRepository, user_id: int, organization_id: int | None, roles
    ) -> AccountOwner:
        """The account the user may read: own, or the organization's for these roles."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _owner(user_id: int, organization_id: int | None) -> AccountOwner:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @asynccontextmanager
    async def _repository(self) -> AsyncIterator[BillingRepository]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")
