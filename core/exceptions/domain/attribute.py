from .domain import BaseDomainServiceError


class AttributeServiceError(BaseDomainServiceError):
    """General error"""

    pass


class AttributeCreationError(AttributeServiceError):
    """Error when creating Attribute in the system."""

    pass


class AttributeGetError(AttributeServiceError):
    """Error when creating Attribute in the system."""

    pass


class AttributeEditError(AttributeServiceError):
    """Error when editing Attribute in the system."""

    pass


class AttributeDeleteError(AttributeServiceError):
    """Error when deleting a Attribute in the system."""

    pass


class AnalogAttributeGetError(AttributeServiceError):
    """Error when creating Analog Attribute in the system."""

    pass


class PatentAttributeGetError(AttributeServiceError):
    """Error when creating Patent Attribute in the system."""

    pass


class AnalogAttributeAssociationCreationError(AttributeServiceError):
    """Error when creating Analog Attribute in the system."""

    pass


class AnalogAttributeAssociationGetError(AttributeServiceError):
    """Error when creating Analog Attribute in the system."""

    pass


class AnalogAttributeAssociationEditError(AttributeServiceError):
    """Error when editing Analog Attribute in the system."""

    pass


class AnalogAttributeAssociationDeleteError(AttributeServiceError):
    """Error when deleting a Analog Attribute in the system."""

    pass


class PatentAttributeAssociationCreationError(AttributeServiceError):
    """Error when creating Patent Attribute in the system."""

    pass


class PatentAttributeAssociationGetError(AttributeServiceError):
    """Error when creating Patent Attribute in the system."""

    pass


class PatentAttributeAssociationEditError(AttributeServiceError):
    """Error when editing Patent Attribute in the system."""

    pass


class PatentAttributeAssociationDeleteError(AttributeServiceError):
    """Error when deleting a Patent Attribute in the system."""

    pass
