"""YooKassa API v3: create a payment and read its state.

https://yookassa.ru/developers/api
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import aiohttp

from core import logger
from core.enum.billing import PaymentStatus
from core.exceptions import PaymentProviderError
from core.settings import YooKassaSettings

logger = logger.get_logger(__name__)


def to_rub(kopecks: int) -> str:
    """Amount as YooKassa wants it: "100.00"."""
    raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


def to_kopecks(value: str) -> int:
    raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


@dataclass(frozen=True)
class ProviderPayment:
    id: str
    status: PaymentStatus
    amount: int
    currency: str
    confirmation_url: str | None = None


@dataclass(frozen=True)
class ProviderRefund:
    id: str
    status: str  # pending, succeeded, canceled
    amount: int


class YooKassaClient:
    def __init__(self, settings: YooKassaSettings):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def create_payment(
        self,
        amount: int,
        idempotence_key: str,
        return_url: str,
        description: str,
        customer_email: str | None,
    ) -> ProviderPayment:
        """Create a payment captured at once; the user pays on ``confirmation_url``.

        ``idempotence_key`` makes a repeated request return the same payment.
        """
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def get_payment(self, payment_id: str) -> ProviderPayment:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def create_refund(
        self,
        payment_id: str,
        amount: int,
        idempotence_key: str,
        customer_email: str | None,
    ) -> ProviderRefund:
        """Return ``amount`` of the payment; the same key returns the same refund."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def get_refund(self, refund_id: str) -> ProviderRefund:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def _receipt(self, amount: int, customer_email: str | None) -> dict[str, Any] | None:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _parse_refund(data: dict[str, Any]) -> ProviderRefund:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    @staticmethod
    def _parse(data: dict[str, Any]) -> ProviderPayment:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")
