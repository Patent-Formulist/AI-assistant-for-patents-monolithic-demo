from .domain import BaseDomainServiceError


class AnalogServiceError(BaseDomainServiceError):
    """General error"""

    pass


class AnalogLinkServiceError(BaseDomainServiceError):
    """General error"""

    pass


class AnalogCreationLinkError(AnalogLinkServiceError):
    """Error when creating analog link in the system."""

    pass


class AnalogEditLinkError(AnalogLinkServiceError):
    """Error when edit analog link in the system."""

    pass


class AnalogCreationError(AnalogServiceError):
    """Error when creating analog in the system."""

    pass


class AnalogGetError(AnalogServiceError):
    """Error when creating analog in the system."""

    pass


class AnalogNotFoundError(AnalogGetError):
    """Analog does not exist or is soft deleted."""

    pass


class AnalogEditError(AnalogServiceError):
    """Error when editing analog in the system."""

    pass


class AnalogDeleteError(AnalogServiceError):
    """Error when deleting a analog in the system."""

    pass
