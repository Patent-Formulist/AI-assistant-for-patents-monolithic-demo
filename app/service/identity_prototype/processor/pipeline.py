from app.service.billing.billing import BillingService
from app.service.job.job import JobService
from app.service.pipeline_preconditions import PipelinePreconditions
from app.service.processor import PipelineStarter
from app.service.task.task import TaskService
from app.temporal.client import WorkflowStarter
from app.temporal.workflows.identity import TASK_IDENTITY_GENERATION, IdentityWorkflow
from core.enum.job_type import JobType


class ProcessorIdentityPipelineService(PipelineStarter):
    """Starts identity prototype generation as a Temporal workflow (ADR 0005)."""

    def __init__(
        self,
        job_service: JobService,
        task_service: TaskService,
        workflow_starter: WorkflowStarter,
        billing: BillingService,
        preconditions: PipelinePreconditions,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def run_identity_pipeline(self, user_id: int, patent_id: int) -> int:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
