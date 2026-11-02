from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.service.base import BaseService
from app.service.job.repository import JobRepository
from core.data_mapper.job import JobMapper
from core.db.models.job import JobModel
from core.domain.job import Job
from core.enum.job_type import JobType
from core.exceptions import (
    JobServiceCreationError,
    JobServiceEditError,
    JobServiceGetError,
)


class _JobStore(BaseService[JobModel, JobRepository]):
    repository_type = JobRepository


class JobService:
    """Job status storage.

    Every call runs in its own short session and commits on its own, so a
    status change never commits (or is rolled back with) the processor's
    business transaction. See ADR 0002.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create_job(self, job: Job) -> Job:
        with BaseService.raise_as(JobServiceCreationError, "Failed to create job"):
            async with self._store() as store:
                model = await store.create(await JobMapper.to_model(job))
                return await JobMapper.to_domain(model)

    async def get_job(self, job_id: int) -> Job:
        with BaseService.raise_as(JobServiceGetError, f"Failed to get job {job_id}"):
            async with self._store() as store:
                return await JobMapper.to_domain(await store.get(job_id))

    async def delete_job(self, job_id: int) -> None:
        """Delete the job with its tasks: for a job that never started."""
        with BaseService.raise_as(JobServiceEditError, f"Failed to delete job {job_id}"):
            async with self._store() as store:
                await store.delete(job_id)

    async def save_job(self, job: Job) -> None:
        """Persist the job state (status, error, result, timestamps, stage)."""
        # Through the mapper: the domain keeps the stage in `_current_stage`, and
        # None must overwrite here (e.g. a cleared error), so dumping the
        # dataclass with exclude_none would not do.
        with BaseService.raise_as(JobServiceEditError, f"Failed to save job {job.id}"):
            async with self._store() as store:
                await store.update(await JobMapper.to_model(job), item_id=job.id)

    async def get_latest_jobs_by_patent(
        self, patent_id: int, job_types: Sequence[JobType]
    ) -> dict[JobType, Job]:
        """The most recent job of each of ``job_types`` for a patent, if any."""
        with BaseService.raise_as(
            JobServiceGetError, f"Failed to get latest jobs for patent {patent_id}"
        ):
            async with self._store() as store:
                models = await store.repository.list_latest_by_patent(patent_id, job_types)
                return {JobType(m.job_type): await JobMapper.to_domain(m) for m in models}

    @asynccontextmanager
    async def _store(self) -> AsyncIterator[_JobStore]:
        async with self._session_factory() as session:
            yield _JobStore(session=session)
            await session.commit()
