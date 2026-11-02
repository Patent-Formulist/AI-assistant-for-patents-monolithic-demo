from .domain import BaseDomainServiceError


# Analog
class AnalogAttributeSignError(BaseDomainServiceError):
    pass


class AnalogAttributeSignCreationError(AnalogAttributeSignError):
    pass


class AnalogAttributeSignDeleteError(AnalogAttributeSignError):
    pass


# Patent
class PatentAttributeSignError(BaseDomainServiceError):
    pass


class PatentAttributeSignCreationError(AnalogAttributeSignError):
    pass


class PatentAttributeSignDeleteError(AnalogAttributeSignError):
    pass
