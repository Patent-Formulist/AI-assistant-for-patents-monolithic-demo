class BillingError(Exception):
    """Base of billing errors."""


class InsufficientFundsError(BillingError):
    """Not enough money for the operation (API answers 402).

    The message is shown to the user as is.
    """


class AccessDeniedError(Exception):
    """The user may not do this (API answers 403)."""


class PaymentsDisabledError(BillingError):
    """Payments are not configured (API answers 503)."""


class PaymentNotFoundError(BillingError):
    """No such payment of the user (API answers 404)."""


class PaymentProviderError(BillingError):
    """The payment provider failed or refused (API answers 502)."""
