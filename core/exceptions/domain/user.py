class UserError(Exception):
    """Base class for user errors."""

    pass


class RegistrationError(UserError):
    pass


class LoginError(UserError):
    pass


class LogoutError(UserError):
    pass


class MissingHeaderError(UserError):
    pass


class InvalidSchemeError(UserError):
    pass
