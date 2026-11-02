class KeyError(Exception):
    pass


class ErrorUnableToUseLimit(KeyError):
    pass


class NoAvailableKeysException(KeyError):
    """Raised when no keys with available limit are found"""

    pass
