from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.service.base import BaseService
from app.service.task.repository import TaskRepository
from core.data_mapper.task.task import TaskMapper
from core.data_mapper.task.tasks import TasksMapper
from core.db.models.task import TaskModel
from core.domain.task import Task
from core.exceptions import (
    TaskServiceCreationError,
    TaskServiceEditError,
    TaskServiceGetError,
)


class _TaskStore(BaseService[TaskModel, TaskRepository]):
    repository_type = TaskRepository


class TaskService:
    """Task status storage; every call commits in its own session (ADR 0002)."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create_task(self, task: Task) -> Task:
        with BaseService.raise_as(TaskServiceCreationError, f"Failed to create task {task.name}"):
            async with self._store() as store:
                return await TaskMapper.to_domain(await store.create(task))

    async def get_tasks_by_job(self, job_id: int) -> list[Task]:
        with BaseService.raise_as(TaskServiceGetError, f"Failed to get tasks of job {job_id}"):
            async with self._store() as store:
                models = await store.repository.list_by_job(job_id)
                return await TasksMapper.to_domain(list(models))

    async def save_task(self, task: Task) -> None:
        """Persist the task state; fields left as None keep their stored value."""
        with BaseService.raise_as(TaskServiceEditError, f"Failed to save task {task.id}"):
            async with self._store() as store:
                await store.update(task, item_id=task.id)

    @asynccontextmanager
    async def _store(self) -> AsyncIterator[_TaskStore]:
        async with self._session_factory() as session:
            yield _TaskStore(session=session)
            await session.commit()
