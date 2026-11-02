from .domain import BaseDomainServiceError


class AnalogAttributeAssociationServiceError(BaseDomainServiceError):
    pass


class AnalogAttributeAssociationGetError(AnalogAttributeAssociationServiceError):
    pass


class AnalogAttributeAssociationEditError(AnalogAttributeAssociationServiceError):
    pass


class AnalogAttributeAssociationDeleteError(AnalogAttributeAssociationServiceError):
    pass


class AnalogAttributeAssociationCreationError(AnalogAttributeAssociationServiceError):
    pass
