"""
Functions / classes for user profile management
"""

__author__ = "Justin B. (justin@justin.directory)"


from typing import Optional
from uuid import UUID


class AccountProfile:
    """
    The profile of the requested users
    """

    user_id: UUID
    """The OID of the account."""
    first_name: Optional[str]
    """The first name of the account."""
    last_name: Optional[str]
    """The last name of the account."""
    user_name: Optional[str]
    """The chosen username of the account."""
    is_user: bool
    """Whether or not the account is a user."""
    roles: list[str]
    """A list of user roles for the account."""
    scopes: list[str]
    """A list of scopes for the account."""

    def __init__(self, jwt: dict):
        oid = jwt.get("oid")
        assert oid is not None, "Missing oid claim, it is required."
        self.user_id = UUID(oid)
        self.first_name = jwt.get("given_name")
        self.last_name = jwt.get("family_name")
        self.user_name = jwt.get("name")

        # Role string & is_user
        role_string: str = jwt.get("extension_roles")
        self.is_user = jwt.get("extension_uflag") == True
        if role_string is None:
            if self.is_user:
                raise ValueError(
                    "Missing extension_roles claim, it is required for user accounts."
                )
            self.roles = []
        else:
            self.roles = role_string.split(",")

        scope_string: str = jwt.get("scp")
        assert isinstance(
            scope_string, str), "Missing scp claim, it is required."
        self.scopes = scope_string.split(" ")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<UserProfile {self.user_id}>"
