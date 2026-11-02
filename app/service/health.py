import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core import logger

logger = logger.get_logger(__name__)


@dataclass(frozen=True)
class HealthReport:
    # Component -> "ok" or "fail"; details only go to the log
    checks: dict[str, str]

    @property
    def ok(self) -> bool:
        return all(state == "ok" for state in self.checks.values())


class HealthChecker:
    """Checks that the dependencies answer: the database and Temporal.

    Each check has a timeout: a hanging dependency is as bad as a dead one.
    The reason of a failure is logged, never returned: the report is public.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        temporal_client: Callable[[], Awaitable[Any]],
        timeout_seconds: float,
    ):
        self._session_factory = session_factory
        self._temporal_client = temporal_client
        self._timeout = timeout_seconds

    async def check(self) -> HealthReport:
        names = ("database", "temporal")
        results = await asyncio.gather(
            self._run("database", self._database),
            self._run("temporal", self._temporal),
        )
        return HealthReport(checks=dict(zip(names, results, strict=True)))

    async def _run(self, name: str, check: Callable[[], Awaitable[None]]) -> str:
        try:
            await asyncio.wait_for(check(), timeout=self._timeout)
            return "ok"
        except Exception as e:
            logger.error(f"Health check {name} failed: {type(e).__name__}: {e}")
            return "fail"

    async def _database(self) -> None:
        async with self._session_factory() as session:
            await session.execute(text("SELECT 1"))

    async def _temporal(self) -> None:
        client = await self._temporal_client()
        healthy = await client.service_client.check_health(timeout=timedelta(seconds=self._timeout))
        if not healthy:
            raise RuntimeError("Temporal reports not serving")
