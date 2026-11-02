import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.service.billing.billing import BillingService, format_rub
from app.service.legal.legal import ConsentCheck
from app.service.organization.organization import OrganizationService
from app.service.payment.yookassa import ProviderPayment, YooKassaClient
from core import logger
from core.db.models.payment import PaymentModel, RefundModel
from core.db.models.user import UserModel
from core.domain.billing import AccountOwner, Payment, Refund
from core.enum.billing import PaymentStatus, RefundStatus
from core.exceptions import (
    AccessDeniedError,
    PaymentNotFoundError,
    PaymentProviderError,
    PaymentsDisabledError,
)
from core.settings import PaymentSettings

logger = logger.get_logger(__name__)

PROVIDER = "yookassa"
FINAL = (PaymentStatus.SUCCEEDED, PaymentStatus.CANCELED)


def _external_id(provider_payment_id: str) -> str:
    raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


class PaymentService:
    """Balance top-ups through YooKassa.

    The user pays on the provider's page; the balance grows only when the
    provider itself says the payment succeeded: a notification is only a hint
    to ask YooKassa for the payment, its body is never trusted. Crediting is
    idempotent (the ledger entry is keyed by the provider payment id), so a
    repeated notification and a status check racing it credit once.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        billing: BillingService,
        client: YooKassaClient,
        settings: PaymentSettings,
        consents: ConsentCheck | None = None,
    ):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def create(
        self, user_id: int, amount: int, organization_id: int | None = None
    ) -> Payment:
        """Start a top-up of ``amount`` kopecks; the user pays on ``confirmation_url``.

        With ``organization_id`` the money goes to that organization's account:
        any member may top it up.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def get(self, user_id: int, payment_id: int) -> Payment:
        """The user's payment; a pending one is checked with the provider first."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def recent(self, user_id: int, limit: int = 20) -> list[Payment]:
        """The user's payments, newest first, as stored (no provider check)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _read(self, user_id: int, payment_id: int) -> tuple[Payment, str]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def sync(self, provider_payment_id: str) -> None:
        """Bring the payment to the provider's state; credit the balance on success.

        Called for a provider notification: unknown payments are ignored.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _credit(
        self, owner: AccountOwner, user_id: int, expected: int, actual: ProviderPayment
    ) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    # ---------- Refunds (administrators) ----------

    async def refund(self, admin_id: int, payment_id: int, amount: int | None = None) -> Refund:
        """Return money of a succeeded payment to the card it came from.

        ``amount`` defaults to what is left of the payment. Only money still on
        the balance can be returned. The balance is debited first, then
        YooKassa is asked; if it refuses, the money goes back on the balance.
        If YooKassa does not answer, the refund stays CREATED and
        ``sync_refund`` asks again with the same idempotence key.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def sync_refund(self, admin_id: int, refund_id: int) -> Refund:
        """Bring a refund to YooKassa's state: ask again if it was never accepted."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _ask_provider(self, refund_id: int) -> Refund:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _set_refund(
        self, refund_id: int, status: RefundStatus, provider_refund_id: str | None = None
    ) -> Refund:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    async def _require_admin(session: AsyncSession, user_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _owner(user_id: int, organization_id: int | None) -> AccountOwner:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _refund(model: RefundModel) -> Refund:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def _check_enabled(self) -> None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _domain(model: PaymentModel) -> Payment:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[AsyncSession]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")
