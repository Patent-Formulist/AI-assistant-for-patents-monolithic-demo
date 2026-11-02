from .domain import BaseDomainServiceError


class AnalogStatisticsServiceError(BaseDomainServiceError):
    """General error"""

    pass


class AnalogAttributeCreationError(BaseDomainServiceError):
    """Error when creating analog attribute in the system."""

    pass


class MatchingAnalogAttributeCreationError(BaseDomainServiceError):
    """Error when creating matching analog attribute in the system."""

    pass


class PatentAttributeCreationError(BaseDomainServiceError):
    """Error when creating patent attribute in the system."""

    pass


class GeneralAttributeCreationError(BaseDomainServiceError):
    """Error when creating general attribute in the system."""

    pass


class PatentSignGetError(BaseDomainServiceError):
    pass


class AnalogSignGetError(BaseDomainServiceError):
    pass


class GeneralSignGetError(BaseDomainServiceError):
    pass


class MatchingAnalogGetError(BaseDomainServiceError):
    """Error when creating matching analog attribute in the system."""

    pass


class CoincidenceGetError(BaseDomainServiceError):
    pass


class AnalogStatisticsError(Exception):
    pass
