class ServiceError(Exception):
    """Base class for service-level errors."""

    pass


class ServiceDataError(ServiceError):
    """Error at the data service level"""

    pass


class DatInputError(ServiceDataError):
    """Error in the input data in the data service"""

    pass


class ServiceRawDataGeneratorError(ServiceError):
    """Exception raised for errors at the raw data service level."""

    pass
