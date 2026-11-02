from core.dependencies.dependencies import get_session_factory


def get_job_service():
    from app.service.job.job import JobService

    return JobService(session_factory=get_session_factory())
