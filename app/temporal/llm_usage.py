"""Stores the LLM token usage of every pipeline step attempt (worker side)."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from temporalio import activity
from temporalio.worker import (
    ActivityInboundInterceptor,
    ExecuteActivityInput,
    Interceptor,
)

from app.service.llm_usage.collector import LLMUsage, collect_usage
from app.service.llm_usage.repository import LLMUsageRepository
from app.temporal import shared
from core import logger

logger = logger.get_logger(__name__)


@dataclass(frozen=True)
class StepUsage:
    """LLM usage of one attempt of a pipeline step."""

    job_id: int
    task_name: str
    attempt: int
    succeeded: bool
    records: list[LLMUsage]


UsageStore = Callable[[StepUsage], Awaitable[None]]


def database_usage_store(session_factory: async_sessionmaker[AsyncSession]) -> UsageStore:
    async def store(usage: StepUsage) -> None:
        async with session_factory() as session:
            await LLMUsageRepository(session=session).add_step_usage(
                usage.job_id, usage.task_name, usage.attempt, usage.succeeded, usage.records
            )
            await session.commit()

    return store


class LLMUsageInterceptor(Interceptor):
    """Collects the LLM usage of each step attempt and stores it when the attempt ends.

    The step is known from the activity ID (``shared.step_activity_id``). Usage is
    stored whether the attempt succeeded or failed: the provider bills every
    response.
    """

    def __init__(self, store: UsageStore):
        self._store = store

    def intercept_activity(self, next: ActivityInboundInterceptor) -> ActivityInboundInterceptor:
        return _CollectUsage(next, self._store)


class _CollectUsage(ActivityInboundInterceptor):
    def __init__(self, next: ActivityInboundInterceptor, store: UsageStore):
        super().__init__(next)
        self._store = store

    async def execute_activity(self, input: ExecuteActivityInput) -> Any:
        info = activity.info()
        step = shared.parse_step_activity_id(info.activity_id)
        if step is None:
            return await super().execute_activity(input)
        job_id, task_name = step
        succeeded = False
        with collect_usage() as usage:
            try:
                result = await super().execute_activity(input)
                succeeded = True
                return result
            finally:
                if usage.records:
                    await self._save(
                        StepUsage(job_id, task_name, info.attempt, succeeded, usage.records)
                    )

    async def _save(self, usage: StepUsage) -> None:
        try:
            await self._store(usage)
        except Exception:
            # Losing the record must not fail the step: a retry would bill the LLM again
            logger.exception(
                f"Failed to store LLM usage of job {usage.job_id} step {usage.task_name}"
            )
