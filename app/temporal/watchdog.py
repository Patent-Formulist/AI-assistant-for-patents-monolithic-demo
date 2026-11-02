"""Worker-side watchdog: periodic checks of states that need a person.

Runs next to the Temporal workers. Each check is a query; what it finds goes
to the administrators through AlertService (which drops repeats).
"""

import asyncio
from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.service.alerts import AlertService
from app.service.billing.billing import format_rub
from core import logger
from core.db.models.billing import BillingHoldModel
from core.db.models.key import KeyModel
from core.db.models.payment import RefundModel
from core.enum.billing import HoldStatus, RefundStatus
from core.enum.token_key import KeyType
from core.settings import MonitoringSettings

logger = logger.get_logger(__name__)


class Watchdog:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        alerts: AlertService,
        settings: MonitoringSettings,
    ):
        self._session_factory = session_factory
        self._alerts = alerts
        self._settings = settings

    async def run(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            await self.check()
            try:
                await asyncio.wait_for(stop.wait(), timeout=self._settings.watchdog_seconds)
            except TimeoutError:
                pass

    async def check(self) -> None:
        for check in (self._stuck_refunds, self._expired_holds, self._llm_keys):
            try:
                await check()
            except Exception as e:
                # One broken check must not stop the others or the worker
                logger.error(f"Watchdog check {check.__name__} failed: {e}")

    async def _stuck_refunds(self) -> None:
        async with self._session_factory() as session:
            refunds = (
                await session.scalars(
                    select(RefundModel).where(
                        RefundModel.status.in_([RefundStatus.CREATED, RefundStatus.PENDING]),
                        RefundModel.created_at
                        < func.now() - timedelta(minutes=self._settings.refund_stuck_minutes),
                    )
                )
            ).all()
        for refund in refunds:
            await self._alerts.alert(
                f"refund:{refund.id}",
                f"💸 Возврат #{refund.id} на {format_rub(refund.amount)} не завершён "
                f"({refund.status.value}). Деньги списаны с баланса и ждут ЮKassa: "
                f"POST /api/v2/billing/refunds/{refund.id}/sync",
            )

    async def _expired_holds(self) -> None:
        """Holds past their expiry: the workflow ended without a final status."""
        async with self._session_factory() as session:
            holds = (
                await session.execute(
                    update(BillingHoldModel)
                    .where(
                        BillingHoldModel.status == HoldStatus.HELD,
                        BillingHoldModel.expires_at < func.now(),
                    )
                    .values(status=HoldStatus.RELEASED, settled_at=func.now())
                    .returning(
                        BillingHoldModel.id, BillingHoldModel.job_id, BillingHoldModel.amount
                    )
                )
            ).all()
            await session.commit()
        for hold_id, job_id, amount in holds:
            await self._alerts.alert(
                f"hold:{hold_id}",
                f"⏱ Резерв {format_rub(amount)} для job {job_id} истёк без финального статуса: "
                "workflow завершён таймаутом или вручную. Резерв снят, деньги не списаны; "
                "проверьте job и Temporal UI.",
            )

    async def _llm_keys(self) -> None:
        async with self._session_factory() as session:
            last_expiry = await session.scalar(
                select(func.max(KeyModel.expires_at)).where(
                    KeyModel.key_type == KeyType.DeepSeek,
                    KeyModel.revoked.is_not(True),
                    KeyModel.expires_at > func.now(),
                )
            )
            soon = await session.scalar(
                select(func.now() + timedelta(days=self._settings.llm_key_warning_days))
            )
        if last_expiry is None:
            await self._alerts.alert(
                "llm-keys:none",
                "🔑 Нет действующих ключей DeepSeek: пайплайны с LLM падают. "
                "Добавьте ключ: scripts/add_key.py",
            )
        elif last_expiry < soon:
            await self._alerts.alert(
                "llm-keys:expiring",
                f"🔑 Последний ключ DeepSeek истекает {last_expiry:%Y-%m-%d %H:%M}. "
                "Добавьте новый: scripts/add_key.py",
            )
