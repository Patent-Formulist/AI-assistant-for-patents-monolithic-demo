from core.data_mapper.mapper import StaticMapper
from core.db.models.job import JobModel
from core.domain.job import Job
from core.enum.job_status import JobStatus
from core.enum.job_type import JobType


class JobMapper(StaticMapper[Job, JobModel, None]):
    @staticmethod
    async def to_model(job: Job) -> JobModel:
        model = JobModel()
        if job.id is not None:
            model.id = job.id
        model.user_id = job.user_id
        model.patent_id = job.patent_id
        model.job_type = job.job_type.value
        model.status = job.status.value
        model.error = job.error
        model.result = job.result
        model.started_at = job.started_at
        model.completed_at = job.completed_at
        model.current_stage = job._current_stage
        return model

    @staticmethod
    async def to_domain(model: JobModel) -> Job:
        job = Job(
            user_id=model.user_id,
            patent_id=model.patent_id,
            job_type=JobType(model.job_type),
            id=model.id,
            status=JobStatus(model.status),
            error=model.error,
            result=model.result,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )
        if model.current_stage:
            job.current_stage = model.current_stage
        return job
