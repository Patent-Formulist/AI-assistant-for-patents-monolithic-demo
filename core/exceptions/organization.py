class OrganizationNotFoundError(Exception):
    """No such organization, member or invitation visible to the user (API answers 404)."""


class OrganizationConflictError(Exception):
    """The change contradicts the current state: already a member, the owner leaving (409)."""
