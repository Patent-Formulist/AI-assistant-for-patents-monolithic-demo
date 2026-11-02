class EmailVerificationError(Exception):
    """The confirmation link is invalid, expired or for another email (API answers 400)."""


class EmailNotVerifiedError(Exception):
    """The action needs a confirmed email (API answers 403)."""


class TooManyRequestsError(Exception):
    """Asked again too soon (API answers 429)."""
