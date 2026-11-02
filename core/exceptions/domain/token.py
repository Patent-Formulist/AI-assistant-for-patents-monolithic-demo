class TokenError(Exception):
    """Base class for token errors."""

    pass


class AccessTokenError(TokenError):
    pass


class RefreshTokenError(TokenError):
    pass


class ValidationTokenError(TokenError):
    pass
