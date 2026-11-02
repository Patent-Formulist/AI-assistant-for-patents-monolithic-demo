from .analog import (
    AnalogCreationError,
    AnalogDeleteError,
    AnalogEditError,
    AnalogGetError,
    AnalogNotFoundError,
    AnalogServiceError,
)
from .analog_attribute_association import (
    AnalogAttributeAssociationCreationError,
    AnalogAttributeAssociationDeleteError,
    AnalogAttributeAssociationEditError,
    AnalogAttributeAssociationGetError,
    AnalogAttributeAssociationServiceError,
)
from .analog_link import (
    AnalogCreationLinkError,
    AnalogEditLinkError,
    AnalogGetLinkError,
    AnalogLinkServiceError,
)
from .attribute import (
    AnalogAttributeGetError,
    AttributeCreationError,
    AttributeDeleteError,
    AttributeEditError,
    AttributeGetError,
    AttributeServiceError,
    PatentAttributeGetError,
)
from .coincidence import (
    AnalogAttributeSignCreationError,
    AnalogAttributeSignDeleteError,
    AnalogAttributeSignError,
    PatentAttributeSignCreationError,
    PatentAttributeSignDeleteError,
    PatentAttributeSignError,
)
from .domain import BaseDomainServiceError
from .identity_prototype import (
    IdentifyPrototypeCreationError,
    IdentifyPrototypeDeleteError,
    IdentifyPrototypeEditError,
    IdentifyPrototypeGetError,
    IdentifyPrototypeServiceError,
)
from .job import (
    JobServiceCreationError,
    JobServiceDeleteError,
    JobServiceEditError,
    JobServiceError,
    JobServiceGetError,
)
from .key import (
    ErrorUnableToUseLimit,
    NoAvailableKeysException,
)
from .patent import (
    PatentAttributeCreationError,
    PatentCreationError,
    PatentDeleteError,
    PatentEditError,
    PatentGetError,
    PatentNotFoundError,
    PatentServiceError,
)
from .patent_attribute_association import (
    PatentAttributeAssociationCreationError,
    PatentAttributeAssociationDeleteError,
    PatentAttributeAssociationEditError,
    PatentAttributeAssociationGetError,
    PatentAttributeAssociationServiceError,
)
from .statistics import (
    AnalogAttributeCreationError,
    AnalogSignGetError,
    AnalogStatisticsServiceError,
    CoincidenceGetError,
    GeneralAttributeCreationError,
    GeneralSignGetError,
    MatchingAnalogAttributeCreationError,
    MatchingAnalogGetError,
    PatentSignGetError,
)
from .task import (
    TaskServiceCreationError,
    TaskServiceDeleteError,
    TaskServiceEditError,
    TaskServiceError,
    TaskServiceGetError,
)
from .token import (
    AccessTokenError,
    RefreshTokenError,
    TokenError,
    ValidationTokenError,
)
from .user import (
    InvalidSchemeError,
    LoginError,
    LogoutError,
    MissingHeaderError,
    RegistrationError,
    UserError,
)

__all__ = [
    "BaseDomainServiceError",
    # Patent
    "PatentServiceError",
    "PatentGetError",
    "PatentNotFoundError",
    "PatentEditError",
    "PatentDeleteError",
    "PatentCreationError",
    # Analog
    "AnalogServiceError",
    "AnalogGetError",
    "AnalogNotFoundError",
    "AnalogEditError",
    "AnalogDeleteError",
    "AnalogCreationError",
    # Analog Link
    "AnalogLinkServiceError",
    "AnalogGetLinkError",
    "AnalogCreationLinkError",
    "AnalogEditLinkError",
    # Attribute
    "AttributeServiceError",
    "AttributeGetError",
    "AttributeEditError",
    "AttributeDeleteError",
    "AttributeCreationError",
    # Analog Attribute Association
    "AnalogAttributeAssociationServiceError",
    "AnalogAttributeAssociationGetError",
    "AnalogAttributeAssociationEditError",
    "AnalogAttributeAssociationDeleteError",
    "AnalogAttributeAssociationCreationError",
    # Patent Attribute Association
    "PatentAttributeAssociationServiceError",
    "PatentAttributeAssociationGetError",
    "PatentAttributeAssociationEditError",
    "PatentAttributeAssociationDeleteError",
    "PatentAttributeAssociationCreationError",
    # Token
    "TokenError",
    "AccessTokenError",
    "RefreshTokenError",
    "ValidationTokenError",
    # User
    "UserError",
    "LoginError",
    "LogoutError",
    "RegistrationError",
    "InvalidSchemeError",
    "MissingHeaderError",
    # Identity_prototype
    "IdentifyPrototypeServiceError",
    "IdentifyPrototypeGetError",
    "IdentifyPrototypeEditError",
    "IdentifyPrototypeDeleteError",
    "IdentifyPrototypeCreationError",
    # Statistics
    "AnalogStatisticsServiceError",
    "AnalogAttributeCreationError",
    "MatchingAnalogAttributeCreationError",
    "PatentAttributeCreationError",
    "GeneralAttributeCreationError",
    "PatentSignGetError",
    "AnalogSignGetError",
    "GeneralSignGetError",
    "MatchingAnalogGetError",
    "AnalogAttributeGetError",
    "PatentAttributeGetError",
    # Sign
    "AnalogAttributeSignError",
    "AnalogAttributeSignCreationError",
    "AnalogAttributeSignDeleteError",
    "PatentAttributeSignError",
    "PatentAttributeSignCreationError",
    "PatentAttributeSignDeleteError",
    # Job
    "JobServiceError",
    "JobServiceCreationError",
    "JobServiceGetError",
    "JobServiceEditError",
    "JobServiceDeleteError",
    # Task
    "TaskServiceError",
    "TaskServiceCreationError",
    "TaskServiceGetError",
    "TaskServiceEditError",
    "TaskServiceDeleteError",
    # Coincidence
    "CoincidenceGetError",
    # Key
    "ErrorUnableToUseLimit",
    "NoAvailableKeysException",
]
