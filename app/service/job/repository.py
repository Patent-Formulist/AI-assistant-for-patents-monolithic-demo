from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select

from core.db.models.job import JobModel
from core.enum.job_type import JobType


class JobRepository(SQLAlchemyAsyncRepository[JobModel]):
    model_type = JobModel

    async def list_latest_by_patent(
        self, patent_id: int, job_types: Sequence[JobType]
    ) -> Sequence[JobModel]:
        """The most recent job of each of the given types for a patent."""
        return await self.list(
            statement=select(JobModel)
            .where(JobModel.patent_id == patent_id, JobModel.job_type.in_(list(job_types)))
            .distinct(JobModel.job_type)
            .order_by(JobModel.job_type, JobModel.id.desc())
        )
