from .domain import BaseDomainServiceError


class PatentAttributeAssociationServiceError(BaseDomainServiceError):
    pass


class PatentAttributeAssociationGetError(PatentAttributeAssociationServiceError):
    pass


class PatentAttributeAssociationEditError(PatentAttributeAssociationServiceError):
    pass


class PatentAttributeAssociationDeleteError(PatentAttributeAssociationServiceError):
    pass


class PatentAttributeAssociationCreationError(PatentAttributeAssociationServiceError):
    pass
