class LegalDocumentNotFoundError(Exception):
    """No such legal document or version (API answers 404)."""


class ConsentVersionError(Exception):
    """Consent to a version that is not the current one (API answers 409)."""


class ConsentRequiredError(Exception):
    """The user has not accepted the current editions of required documents (API answers 403).

    The message names them and is shown to the user as is.
    """
