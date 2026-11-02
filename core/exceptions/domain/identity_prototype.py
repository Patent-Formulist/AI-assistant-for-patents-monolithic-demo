from .domain import BaseDomainServiceError


class IdentifyPrototypeServiceError(BaseDomainServiceError):
    pass


class IdentifyPrototypeCreationError(IdentifyPrototypeServiceError):
    pass


class IdentifyPrototypeEditError(IdentifyPrototypeServiceError):
    pass


class IdentifyPrototypeGetError(IdentifyPrototypeServiceError):
    pass


class IdentifyPrototypeDeleteError(IdentifyPrototypeServiceError):
    pass
