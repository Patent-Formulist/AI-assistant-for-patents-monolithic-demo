from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select

from app.service.llm_usage.collector import LLMUsage
from core.db.models.job import JobModel
from core.db.models.llm_usage import LLMUsageModel
from core.db.models.task import TaskModel


class LLMUsageRepository(SQLAlchemyAsyncRepository[LLMUsageModel]):
    model_type = LLMUsageModel

    async def add_step_usage(
        self,
        job_id: int,
        step: str,
        attempt: int,
        succeeded: bool,
        records: Sequence[LLMUsage],
    ) -> None:
        """Store the usage of one attempt of a pipeline step, owned by its job's user."""
        job = await self.session.get(JobModel, job_id)
        task_id = await self.session.scalar(
            select(TaskModel.id).where(TaskModel.job_id == job_id, TaskModel.name == step)
        )
        await self.add_many(
            [
                LLMUsageModel(
                    user_id=job.user_id if job else None,
                    patent_id=job.patent_id if job else None,
                    job_id=job.id if job else None,
                    task_id=task_id,
                    step=step,
                    attempt=attempt,
                    succeeded=succeeded,
                    model=usage.model,
                    key_id=usage.key_id,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    cached_tokens=usage.cached_tokens,
                )
                for usage in records
            ]
        )
