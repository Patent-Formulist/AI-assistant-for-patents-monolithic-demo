from dataclasses import dataclass, field
from datetime import datetime

from core.enum.task_status import TaskStatus


@dataclass
class Task:
    job_id: int
    name: str
    order: int
    id: int | None = None
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    error: str | None = None
    result: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    meta: dict | None = field(default=None)

    def start(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self):
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.utcnow()

    def fail(self, error: str = None):
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        if error:
            self.error = error
