from app.service.job.job import JobService
from app.service.user_patent_UI_progress.user_patent_UI_progress import (
    UserPatentUIProgressService,
)
from core.domain.job import Job
from core.enum.job_status import JobStatus
from core.enum.job_type import JobType

# Response field -> job type whose latest job gives the state
_STATE_FIELDS = {
    "analogs_search_pipeline_state": JobType.ANALOG_SEARCH,
    "statistics_pipeline_state": JobType.STATISTICS,
    "identity_pipeline_state": JobType.IDENTITY,
}

# Values the progress API returned before ADR 0004: the route wrote RUNNING
# before the job started, and CANCELLED was never produced.
_STATE_VALUES = {
    JobStatus.PENDING: "RUNNING",
    JobStatus.RUNNING: "RUNNING",
    JobStatus.COMPLETED: "COMPLETED",
    JobStatus.FAILED: "FAILED",
    JobStatus.CANCELLED: "FAILED",
}


class PatentProgressQuery:
    """Patent page progress for frontend reload (ADR 0004).

    Pipeline states come from the latest job of each type; only the last
    opened section is stored per user. Keeps the PatentProgressResponse shape.
    """

    def __init__(self, ui_progress_service: UserPatentUIProgressService, job_service: JobService):
        self._ui_progress_service = ui_progress_service
        self._job_service = job_service

    async def get(self, user_id: int, patent_id: int) -> dict[str, str | None]:
        """Empty dict when the user has no active link to the patent."""
        last_ui_button = await self._ui_progress_service.get_last_ui_button(user_id, patent_id)
        if last_ui_button is None:
            return {}

        jobs = await self._job_service.get_latest_jobs_by_patent(
            patent_id, list(_STATE_FIELDS.values())
        )
        progress: dict[str, str | None] = {
            "last_ui_button": last_ui_button.value,
            "statistics_pipeline_stage": None,
            "pipeline_error": self._last_error(jobs.values()),
        }
        for field, job_type in _STATE_FIELDS.items():
            job = jobs.get(job_type)
            progress[field] = _STATE_VALUES[job.status] if job else None
        return progress

    @staticmethod
    def _last_error(jobs) -> str | None:
        latest: Job | None = max(jobs, key=lambda j: j.id, default=None)
        if latest is None:
            return None
        if latest.status in (JobStatus.FAILED, JobStatus.CANCELLED):
            return latest.error or ""
        return ""
