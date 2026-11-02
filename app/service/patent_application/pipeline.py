from app.service.processor import PipelineStarter
from app.temporal.workflows.patent_application import (
    TASK_GENERATE_APPLICATION,
    PatentApplicationWorkflow,
)
from core.enum.job_type import JobType


class ProcessorApplicationPipelineService(PipelineStarter):
    """Starts patent application generation as a Temporal workflow (ADR 0005)."""

    async def run_application_pipeline(self, user_id: int, patent_id: int) -> int:
        """Create the job, start PatentApplicationWorkflow, return the job id."""
        return await self._start_patent_pipeline(
            job_type=JobType.APPLICATION_GENERATION,
            task_definitions=[{"name": TASK_GENERATE_APPLICATION, "order": 0}],
            user_id=user_id,
            patent_id=patent_id,
            workflow_run=PatentApplicationWorkflow.run,
        )
