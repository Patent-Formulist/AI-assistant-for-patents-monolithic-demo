from core.data_mapper.mapper import StaticMapper
from core.db.models.task import TaskModel
from core.domain.task import Task
from core.enum.task_status import TaskStatus


class TaskMapper(StaticMapper[Task, TaskModel, None]):
    @staticmethod
    async def to_model(task: Task) -> TaskModel:
        model = TaskModel()
        if task.id is not None:
            model.id = task.id
        model.job_id = task.job_id
        model.name = task.name
        model.order = task.order
        model.status = task.status.value
        model.progress = task.progress
        model.error = task.error
        model.result = task.result
        model.started_at = task.started_at
        model.completed_at = task.completed_at
        model.meta = task.meta
        return model

    @staticmethod
    async def to_domain(model: TaskModel) -> Task:
        return Task(
            job_id=model.job_id,
            name=model.name,
            order=model.order,
            id=model.id,
            status=TaskStatus(model.status),
            progress=model.progress,
            error=model.error,
            result=model.result,
            started_at=model.started_at,
            completed_at=model.completed_at,
            meta=model.meta,
        )
