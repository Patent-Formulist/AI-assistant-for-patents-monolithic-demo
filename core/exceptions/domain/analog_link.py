from .domain import BaseDomainServiceError


class AnalogLinkServiceError(BaseDomainServiceError):
    """General error"""

    pass


class AnalogGetLinkError(AnalogLinkServiceError):
    """Error when get analog link in the system."""

    pass


class AnalogCreationLinkError(AnalogLinkServiceError):
    """Error when creating analog link in the system."""

    pass


class AnalogEditLinkError(AnalogLinkServiceError):
    """Error when edit analog link in the system."""

    pass
