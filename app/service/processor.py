import time
from collections.abc import Callable, Coroutine
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.exceptions import WorkflowAlreadyStartedError

from app.service.billing.billing import BillingService
from app.service.job.job import JobService
from app.service.task.task import TaskService
from app.temporal.client import RunningPipeline, WorkflowStarter
from app.temporal.shared import PatentPipelineInput, StepOptions, patent_workflow_id
from core import logger
from core.domain.job import Job
from core.domain.task import Task
from core.enum.job_type import JobType
from core.enum.task_status import TaskStatus
from core.exceptions import BaseProcessorError, PipelinePreconditionError

logger = logger.get_logger(__name__)


class UnitOfWork:
    """Explicit transaction boundary over the session shared with the services.

    ``async with uow:`` commits on exit and rolls back on error. Commit also
    returns the connection to the pool, so long LLM calls go between blocks:
    read -> generate -> write (ADR 0002).
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        return False


class Processor:
    """Base for processors on BaseService services (ADR 0002).

    Transactions are explicit ``async with self._uow`` blocks inside the
    operation; ``_run`` only logs timing and wraps failures into the
    processor's domain error.
    """

    def __init__(self, uow: UnitOfWork, error_class: type[Exception] = BaseProcessorError):
        self._uow = uow
        self._error_class = error_class

    async def _run(
        self,
        operation: Callable[..., Coroutine[Any, Any, Any]],
        operation_name: str,
        *args,
        **kwargs,
    ) -> Any:
        logger.info(f"Starting {operation_name}")
        start_time = time.time()
        try:
            result = await operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"Failed {operation_name} after {time.time() - start_time:.2f}s: {e}")
            raise self._error_class(f"{operation_name} failed: {e}") from e
        logger.info(f"Completed {operation_name} in {time.time() - start_time:.2f}s")
        return result


# Workflow type -> what the user sees in "already running" messages
PIPELINE_TITLES = {
    "AnalogSearchWorkflow": "поиск аналогов",
    "StatisticsWorkflow": "расчёт статистики",
    "IdentityWorkflow": "выявление прототипа",
    "PatentApplicationWorkflow": "генерация заявки",
}


class PipelineStarter:
    """Starts a background pipeline: its job and tasks, then the workflow (ADR 0005).

    The job is created first so the UI sees it at once; the workflow then moves
    it through RUNNING to COMPLETED or FAILED. The caller gets the job id
    without waiting for the pipeline.

    Pipelines of a patent run one at a time: all of them use the patent's
    workflow ID. Starting the same pipeline again (same ``key``) while it runs
    returns the running job id, so a double click is not an error; starting a
    different one raises PipelinePreconditionError (API answers 400).

    The price of the tasks that will run is held on the user's balance before
    the start (InsufficientFundsError, 402, if it is short); the workflow's
    final job status charges or releases it.
    """

    def __init__(
        self,
        job_service: JobService,
        task_service: TaskService,
        workflow_starter: WorkflowStarter,
        billing: BillingService,
    ):
        self._job_service = job_service
        self._task_service = task_service
        self._workflow_starter = workflow_starter
        self._billing = billing

    async def _join_running(self, patent_id: int, key: str) -> int | None:
        """Job id of the same pipeline running for the patent, None if nothing runs.

        Raises PipelinePreconditionError when a different pipeline runs.
        """
        running = await self._workflow_starter.running_pipeline(patent_workflow_id(patent_id))
        if running is None:
            return None
        return self._join(running, key)

    async def _start_pipeline(
        self,
        *,
        job_type: JobType,
        task_definitions: list[dict],
        user_id: int,
        patent_id: int,
        workflow_run: Callable[..., Any],
        build_input: Callable[[int, StepOptions], Any],
        key: str | None = None,
    ) -> int:
        """Create the job, start ``workflow_run`` with ``build_input(job_id, step_options)``.

        ``key`` tells repeated requests of one pipeline apart from other
        pipelines (default: the job type). If the workflow cannot be started,
        nothing will ever run the job: it is marked FAILED instead of being left
        PENDING for the UI, and the error is re-raised.
        """
        key = key or job_type.value
        # Checked first so that a joined or refused start leaves no job behind
        if (running_job_id := await self._join_running(patent_id, key)) is not None:
            return running_job_id

        workflow_id = patent_workflow_id(patent_id)
        job_id = await self._create_job_with_tasks(job_type, task_definitions, user_id, patent_id)
        price = self._billing.price(
            t["name"]
            for t in task_definitions
            if t.get("status", TaskStatus.PENDING) != TaskStatus.SKIPPED
        )
        if price:
            try:
                await self._billing.hold(user_id, job_id, price)
            except Exception:
                # Not paid for: the job never runs
                await self._job_service.delete_job(job_id)
                raise
        try:
            await self._workflow_starter.start(
                workflow_run,
                build_input(job_id, self._workflow_starter.step_options()),
                workflow_id=workflow_id,
                memo={"key": key, "job_id": job_id},
            )
        except WorkflowAlreadyStartedError as e:
            # Another request started a pipeline of the patent after the check
            # above. This job never ran: delete it, so the UI (latest job of the
            # type) keeps showing the running one.
            await self._billing.settle(job_id, completed=False)
            await self._job_service.delete_job(job_id)
            running = await self._workflow_starter.running_pipeline(workflow_id)
            if running is None:
                raise PipelinePreconditionError(self._already_running(e.workflow_type)) from e
            return self._join(running, key)
        except Exception as e:
            logger.error(f"Failed to start {job_type.value} workflow for job {job_id}: {e}")
            await self._billing.settle(job_id, completed=False)
            job = await self._job_service.get_job(job_id)
            job.fail(error=f"Failed to start the pipeline: {e}")
            await self._job_service.save_job(job)
            raise
        return job_id

    async def _start_patent_pipeline(
        self,
        *,
        job_type: JobType,
        task_definitions: list[dict],
        user_id: int,
        patent_id: int,
        workflow_run: Callable[..., Any],
    ) -> int:
        """``_start_pipeline`` for workflows taking ``PatentPipelineInput``."""
        return await self._start_pipeline(
            job_type=job_type,
            task_definitions=task_definitions,
            user_id=user_id,
            patent_id=patent_id,
            workflow_run=workflow_run,
            build_input=lambda job_id, step_options: PatentPipelineInput(
                job_id=job_id, patent_id=patent_id, step_options=step_options
            ),
        )

    def _join(self, running: RunningPipeline, key: str) -> int:
        if running.key == key and running.job_id is not None:
            logger.info(f"Pipeline '{key}' already runs as job {running.job_id}: joining it")
            return running.job_id
        raise PipelinePreconditionError(self._already_running(running.workflow_type))

    @staticmethod
    def _already_running(workflow_type: str) -> str:
        title = PIPELINE_TITLES.get(workflow_type, "другой процесс")
        return f"Для этого патента уже выполняется {title}: дождитесь окончания"

    async def _create_job_with_tasks(
        self,
        job_type: JobType,
        task_definitions: list[dict],
        user_id: int,
        patent_id: int,
    ) -> int:
        """Create the Job + Task rows (committed in their own sessions) and return job_id.

        A task definition is ``{"name", "order"}`` plus optional ``"meta"`` and
        ``"status"`` (default PENDING).
        """
        job = Job(user_id=user_id, patent_id=patent_id, job_type=job_type)
        job = await self._job_service.create_job(job)
        job_id = job.id
        logger.info(f"Job {job_id} created (type={job_type.value})")

        for task_def in task_definitions:
            task = Task(
                job_id=job_id,
                name=task_def["name"],
                order=task_def["order"],
                status=task_def.get("status", TaskStatus.PENDING),
                meta=task_def.get("meta"),
            )
            await self._task_service.create_task(task)

        return job_id
