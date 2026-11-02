from .domain import BaseDomainServiceError


class PatentServiceError(BaseDomainServiceError):
    """General error"""

    pass


class PatentAttributeCreationError(PatentServiceError):
    """Error when creating a patent in the system."""

    pass


class PatentAttributeSignCreationError(PatentServiceError):
    """Error when creating a patent in the system."""

    pass


class PatentCreationError(PatentServiceError):
    """Error when creating a patent in the system."""

    pass


class PatentGetError(PatentServiceError):
    """Error when getting a patent from the system."""

    pass


class PatentNotFoundError(PatentGetError):
    """Patent does not exist, is soft deleted or is not linked to the user."""

    pass


class PatentEditError(PatentServiceError):
    """Error when editing a patent in the system."""

    pass


class PatentDeleteError(PatentServiceError):
    """Error when deleting a patent in the system."""

    pass
