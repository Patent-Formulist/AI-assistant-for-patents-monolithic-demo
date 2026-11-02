from .domain import BaseDomainServiceError


class JobServiceError(BaseDomainServiceError):
    """General error"""

    pass


class JobServiceCreationError(JobServiceError):
    """Error when creating a job in the system."""

    pass


class JobServiceGetError(JobServiceError):
    """Error when creating a job in the system."""

    pass


class JobServiceEditError(JobServiceError):
    """Error when editing a job in the system."""

    pass


class JobServiceDeleteError(JobServiceError):
    """Error when deleting a job in the system."""

    pass
