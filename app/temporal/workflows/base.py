from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from app.temporal import shared


def to_timeout(options: shared.ActivityOptions) -> timedelta:
    return timedelta(seconds=options.start_to_close_seconds)


def to_retry_policy(options: shared.ActivityOptions) -> RetryPolicy:
    retry = options.retry
    return RetryPolicy(
        initial_interval=timedelta(seconds=retry.initial_interval_seconds),
        backoff_coefficient=retry.backoff_coefficient,
        maximum_interval=(
            timedelta(seconds=retry.maximum_interval_seconds)
            if retry.maximum_interval_seconds is not None
            else None
        ),
        maximum_attempts=retry.maximum_attempts,
    )


def error_message(error: BaseException) -> str:
    """The root cause message: ActivityError itself only names the failed activity."""
    while isinstance(error, ActivityError) and error.cause is not None:
        error = error.cause
    return str(error)


class PipelineWorkflow:
    """Base for pipeline workflows: mirrors progress to the job/task rows (ADR 0004).

    Subclasses are decorated with ``@workflow.defn`` and call ``_run_job`` from
    their ``@workflow.run`` method, wrapping each step in ``_step``. Status
    writes are activities on the pipelines queue; steps run on the external
    queue unless told otherwise.

    Timeouts and retries come from the ``StepOptions`` passed to ``_run_job``
    (filled from config by the starter), never from config read here.

    Workflow code runs in the Temporal sandbox: no database, network or
    ``app.service`` imports here or in subclasses.
    """

    def __init__(self) -> None:
        self._options = shared.StepOptions()

    async def _run_job[T](
        self, job_id: int, options: shared.StepOptions, body: Callable[[], Awaitable[T]]
    ) -> T:
        """Run the pipeline body as the job: RUNNING, then COMPLETED or FAILED.

        A failure is recorded with its root cause and re-raised, so the
        workflow execution fails too and stays visible in Temporal.
        """
        self._options = options
        await self._status(shared.MARK_JOB_RUNNING, job_id)
        try:
            result = await body()
        except Exception as e:
            await self._status(shared.MARK_JOB_FAILED, job_id, error_message(e))
            raise
        await self._status(shared.MARK_JOB_COMPLETED, job_id)
        return result

    async def _step(
        self,
        job_id: int,
        task_name: str,
        activity_name: str,
        *args: Any,
        result_type: type | None = None,
        task_queue: str = shared.EXTERNAL_TASK_QUEUE,
        options: shared.ActivityOptions | None = None,
    ) -> Any:
        """Run one activity as the job's task ``task_name``: RUNNING, then COMPLETED or FAILED.

        ``options`` overrides the external step options for this one step.
        """
        step_options = options or self._options.external
        await self._status(shared.MARK_TASK_RUNNING, job_id, task_name)
        try:
            result = await workflow.execute_activity(
                activity_name,
                args=list(args),
                activity_id=shared.step_activity_id(job_id, task_name),
                task_queue=task_queue,
                start_to_close_timeout=to_timeout(step_options),
                retry_policy=to_retry_policy(step_options),
                result_type=result_type,
            )
        except Exception as e:
            await self._status(shared.MARK_TASK_FAILED, job_id, task_name, error_message(e))
            raise
        await self._status(shared.MARK_TASK_COMPLETED, job_id, task_name)
        return result

    async def _status(self, activity_name: str, *args: Any) -> None:
        """Write a job/task status through its activity on the workflow's own queue."""
        await workflow.execute_activity(
            activity_name,
            args=list(args),
            start_to_close_timeout=to_timeout(self._options.status),
            retry_policy=to_retry_policy(self._options.status),
        )
