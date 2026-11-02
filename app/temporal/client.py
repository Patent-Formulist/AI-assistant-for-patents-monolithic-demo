import asyncio
from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields
from datetime import timedelta
from typing import Any

from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.service import RPCError, RPCStatusCode

from app.temporal import shared
from core.settings import get_settings

_client: Client | None = None
_client_lock = asyncio.Lock()


async def get_temporal_client() -> Client:
    """Process-wide Temporal client, connected on first use."""
    global _client
    if _client is None:
        async with _client_lock:
            if _client is None:
                settings = get_settings().temporal
                _client = await Client.connect(
                    settings.address,
                    namespace=settings.namespace,
                    data_converter=pydantic_data_converter,
                )
    return _client


def step_options_from_config(steps: Mapping[str, Any]) -> shared.StepOptions:
    """Build StepOptions from ``temporal.steps``; missing values keep the defaults.

    Unknown keys raise TypeError, so a typo in config.yaml fails loudly instead
    of silently keeping a default.
    """
    unknown = set(steps) - {f.name for f in fields(shared.StepOptions)}
    if unknown:
        raise TypeError(f"Unknown temporal.steps groups: {sorted(unknown)}")

    defaults = shared.StepOptions()
    groups = {}
    for group in ("status", "external"):
        default: shared.ActivityOptions = getattr(defaults, group)
        raw = dict(steps.get(group) or {})
        retry = shared.RetryOptions(**{**vars(default.retry), **(raw.pop("retry", None) or {})})
        groups[group] = shared.ActivityOptions(**{**vars(default), **raw, "retry": retry})
    return shared.StepOptions(**groups)


@dataclass(frozen=True)
class RunningPipeline:
    """A workflow running under a patent's ID, with the memo its starter set."""

    workflow_type: str
    # What was started (e.g. "statistics"); equal keys mean the same request
    key: str | None
    job_id: int | None


class WorkflowStarter:
    """Starts pipeline workflows on the pipelines task queue."""

    def __init__(self, client_provider: Callable[[], Any] = get_temporal_client):
        self._client_provider = client_provider

    def step_options(self) -> shared.StepOptions:
        """Activity timeouts and retries for a new workflow, from config.yaml."""
        return step_options_from_config(get_settings().temporal.steps)

    async def running_pipeline(self, workflow_id: str) -> RunningPipeline | None:
        """The workflow running under ``workflow_id``, None if none runs."""
        client = await self._client_provider()
        try:
            description = await client.get_workflow_handle(workflow_id).describe()
        except RPCError as e:
            if e.status == RPCStatusCode.NOT_FOUND:
                return None
            raise
        if description.status != WorkflowExecutionStatus.RUNNING:
            return None
        memo = await description.memo()
        return RunningPipeline(
            workflow_type=description.workflow_type,
            key=memo.get("key"),
            job_id=memo.get("job_id"),
        )

    async def start(
        self,
        workflow_run: Callable[..., Any],
        arg: Any,
        workflow_id: str,
        execution_timeout: timedelta | None = None,
        memo: Mapping[str, Any] | None = None,
    ) -> None:
        """Start the workflow; returns once Temporal has recorded it.

        ``memo`` is stored with the execution and read back by ``running_pipeline``.

        ``execution_timeout`` defaults to ``temporal.workflow_execution_timeout_seconds``.
        It is a last-resort limit for the whole execution: Temporal ends a
        timed-out workflow without running its code, so the job stays RUNNING
        in that case; FAILED is guaranteed by the bounded activity retries and
        timeouts instead.
        """
        if execution_timeout is None:
            execution_timeout = timedelta(
                seconds=get_settings().temporal.workflow_execution_timeout_seconds
            )
        client = await self._client_provider()
        await client.start_workflow(
            workflow_run,
            arg,
            id=workflow_id,
            task_queue=shared.PIPELINES_TASK_QUEUE,
            execution_timeout=execution_timeout,
            memo=memo,
        )
