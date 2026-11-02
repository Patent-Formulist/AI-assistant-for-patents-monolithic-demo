from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select

from core.db.models.task import TaskModel


class TaskRepository(SQLAlchemyAsyncRepository[TaskModel]):
    model_type = TaskModel

    async def list_by_job(self, job_id: int) -> Sequence[TaskModel]:
        return await self.list(
            statement=select(TaskModel).where(TaskModel.job_id == job_id).order_by(TaskModel.order)
        )
