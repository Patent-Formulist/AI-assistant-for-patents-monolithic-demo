from dataclasses import dataclass, field
from datetime import datetime

from core.enum.job_status import JobStatus
from core.enum.job_type import JobType


@dataclass
class Job:
    user_id: int
    patent_id: int
    job_type: JobType
    id: int | None = None
    status: JobStatus = JobStatus.PENDING
    error: str | None = None
    result: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    _current_stage: str | None = field(default=None, repr=False)

    @property
    def current_stage(self) -> str:
        return self._current_stage

    @current_stage.setter
    def current_stage(self, value: str):
        if value and len(value) >= 50:
            raise ValueError("current_stage must be less than 50 characters")
        self._current_stage = value

    def start(self):
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self):
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self, error: str = None):
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        if error:
            self.error = error
