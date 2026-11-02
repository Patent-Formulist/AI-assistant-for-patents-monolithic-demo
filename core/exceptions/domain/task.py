from .domain import BaseDomainServiceError


class TaskServiceError(BaseDomainServiceError):
    """General error"""

    pass


class TaskServiceCreationError(TaskServiceError):
    """Error when creating a Task in the system."""

    pass


class TaskServiceGetError(TaskServiceError):
    """Error when creating a Task in the system."""

    pass


class TaskServiceEditError(TaskServiceError):
    """Error when editing a Task in the system."""

    pass


class TaskServiceDeleteError(TaskServiceError):
    """Error when deleting a Task in the system."""

    pass
