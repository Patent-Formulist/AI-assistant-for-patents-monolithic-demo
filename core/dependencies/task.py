from core.dependencies.dependencies import get_session_factory


def get_task_service():
    from app.service.task.task import TaskService

    return TaskService(session_factory=get_session_factory())
