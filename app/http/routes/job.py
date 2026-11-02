from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.service.job.job import JobService
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.dto import get_user_job_id
from core.dependencies.job import get_job_service
from core.domain.job import Job

router = APIRouter(prefix="/api/v2/job", tags=["Job"])
logger = logger.get_logger(__name__)
JobServiceDep = Annotated[JobService, Depends(get_job_service)]
UserJobIdDep = Annotated[int, Depends(get_user_job_id)]


@auth_doc
@router.get(
    "/{job_id}",
    summary="Get job",
    description="Get job for the authenticated user and returns the job data",
)
@handle_exceptions
async def get_analogs(job_id: UserJobIdDep, job_service: JobServiceDep):
    job: Job = await job_service.get_job(job_id)
    return JSONResponse(
        status_code=200,
        content={
            "task_id": str(job.id),
            "status": job.status.value,
            "data": job.result,
        },
    )
