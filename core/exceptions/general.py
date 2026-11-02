class ValidationError(Exception):
    """Error validating input data or file structure."""

    pass


class ErrorObjectNotFound(Exception):
    pass


class InternalServerErrorException(Exception):
    pass
