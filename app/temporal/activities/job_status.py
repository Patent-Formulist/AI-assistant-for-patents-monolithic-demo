from temporalio import activity
from temporalio.exceptions import ApplicationError

from app.service.alerts import AlertService
from app.service.billing.billing import BillingService
from app.service.job.job import JobService
from app.service.task.task import TaskService
from app.temporal import shared
from core.domain.task import Task


class JobStatusActivities:
    """Job/task statuses for the progress read-model (ADR 0004, ADR 0005).

    Each call writes in its own short session through JobService/TaskService.
    The final job status also settles the job's billing hold: charged when the
    job completed, released when it failed. Settling is idempotent, so retries
    of these activities are safe.
    """

    def __init__(
        self,
        job_service: JobService,
        task_service: TaskService,
        billing: BillingService,
        alerts: AlertService | None = None,
    ):
        self._job_service = job_service
        self._task_service = task_service
        self._billing = billing
        # A job that failed for good is worth a look; None only in tests
        self._alerts = alerts

    @activity.defn(name=shared.MARK_JOB_RUNNING)
    async def mark_job_running(self, job_id: int) -> None:
        job = await self._job_service.get_job(job_id)
        job.start()
        await self._job_service.save_job(job)

    @activity.defn(name=shared.MARK_JOB_COMPLETED)
    async def mark_job_completed(self, job_id: int) -> None:
        await self._billing.settle(job_id, completed=True)
        job = await self._job_service.get_job(job_id)
        job.complete()
        await self._job_service.save_job(job)

    @activity.defn(name=shared.MARK_JOB_FAILED)
    async def mark_job_failed(self, job_id: int, error: str) -> None:
        await self._billing.settle(job_id, completed=False)
        job = await self._job_service.get_job(job_id)
        job.fail(error=error)
        await self._job_service.save_job(job)
        if self._alerts is not None:
            await self._alerts.alert(
                f"job:{job_id}",
                f"❌ Пайплайн {job.job_type.value} упал: job {job_id}, патент {job.patent_id}, "
                f"пользователь {job.user_id}.\n{error[:500]}",
            )

    @activity.defn(name=shared.MARK_TASK_RUNNING)
    async def mark_task_running(self, job_id: int, task_name: str) -> None:
        task = await self._get_task(job_id, task_name)
        task.start()
        await self._task_service.save_task(task)

    @activity.defn(name=shared.MARK_TASK_COMPLETED)
    async def mark_task_completed(self, job_id: int, task_name: str) -> None:
        task = await self._get_task(job_id, task_name)
        task.complete()
        await self._task_service.save_task(task)

    @activity.defn(name=shared.MARK_TASK_FAILED)
    async def mark_task_failed(self, job_id: int, task_name: str, error: str) -> None:
        task = await self._get_task(job_id, task_name)
        task.fail(error=error)
        await self._task_service.save_task(task)

    async def _get_task(self, job_id: int, task_name: str) -> Task:
        for task in await self._task_service.get_tasks_by_job(job_id):
            if task.name == task_name:
                return task
        # The job was created with a different task set: retrying will not help
        raise ApplicationError(f"Task '{task_name}' not found in job {job_id}", non_retryable=True)

    def all(self) -> list:
        return [
            self.mark_job_running,
            self.mark_job_completed,
            self.mark_job_failed,
            self.mark_task_running,
            self.mark_task_completed,
            self.mark_task_failed,
        ]
