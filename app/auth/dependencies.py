"""
A list of FastAPI specific dependencies for usage in dependency injection.
"""

__author__ = "Justin B. (justin@justin.directory)"

from fastapi import Depends, HTTPException, Request


from app.auth.profile import AccountProfile


def get_profile(request: Request) -> AccountProfile:
    """
    Get the user profile from the ASGI request.
    """
    profile: AccountProfile = request.scope["b2c_profile"]
    if profile is None:
        raise HTTPException(status_code=500, detail="Could not find profile.")

    return profile


def has_roles(roles: list[str]):
    """
    Check if the profile has any of the given roles in an array.
    If the account has any of the roles, it will pass.
    If the account is a bot account, it will pass.

    :param roles: The roles to check for.
    :return: A function that checks if the user has the roles.
    """
    if len(roles) == 0:
        raise ValueError("Roles must be provided.")

    def check_roles(profile: AccountProfile = Depends(get_profile)):

        if not profile.is_user:
            # Bots can't have roles - scope validation is enough.
            return True

        if not any(role in profile.roles for role in roles):
            raise HTTPException(
                status_code=403,
                detail="User does not have the required roles."
            )

        return True

    return check_roles


def has_scopes(scopes: list[str]):
    """
    Check if the profile has any of the given scopes in an array.
    If the account has all of the scopes, it will pass.

    :param scopes: The scopes to check for.
    :return: A function that checks if the user has the scopes.
    """
    if len(scopes) == 0:
        raise ValueError("Scopes must be provided.")

    def check_scopes(profile: AccountProfile = Depends(get_profile)):

        if not all(scope in profile.scopes for scope in scopes):
            raise HTTPException(
                status_code=403,
                detail="User does not have the required scopes."
            )

        return True

    return check_scopes
