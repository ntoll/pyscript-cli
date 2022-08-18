"""
Nucleus authentication utilities.

login - log into the Nucleus platform.
get_token - once logged in, get the token for making API calls.
logout - log out of the Nucleus platform (clear the token).

Based upon code found in the conda-cli repos.
"""
import keyring
import requests
from pyscript import DEFAULT_PYSCRIPT_API_HOST


__all__ = [
    "AuthError",
    "login",
    "get_token",
    "logout",
    "get_host",
    "set_host",
]


KEYRING_APP_NAME = "pyscript_cli"


class AuthError(Exception):
    """
    Raised when the user is unable to login to the API.
    """

    pass


def login(username: str, password: str, hostname: str) -> str:
    """
    Go through the process of logging the user into the API host
    so future calls to the command line can use their token, etc...
    """
    token = _get_token_from_api(username, password, hostname)
    _store_token(hostname, token)
    return token


def logout(hostname: str) -> None:
    """
    Log out of the referenced API instance (clear the token).
    """
    _store_token(hostname, "")


def get_token(hostname: str) -> str:
    """
    Return the token for the given hostname.

    Returns a false-y empty string if no token is set (i.e. the user isn't
    logged in).
    """
    keyring.get_password(KEYRING_APP_NAME, hostname)


def get_host() -> str:
    """
    Returns the hostname of the currently active API instance.
    """
    hostname = keyring.get_password(KEYRING_APP_NAME, "host")
    if not hostname:
        hostname = DEFAULT_PYSCRIPT_API_HOST
    return hostname


def set_host(hostname: str) -> None:
    """
    Sets the hostname of the currently active API default.
    """
    keyring.set_password(KEYRING_APP_NAME, "host", hostname)


def _get_token_from_api(username, password, hostname):
    """
    Get the JWT token from the API at the specified hostname, for the
    referenced user.
    """
    url = f"{hostname}/auth/login"
    response = requests.post(
        url,
        json={
            "username": username,
            "password": password,
        },
    )
    if response.status_code != 200:
        raise AuthError(f"{response.status_code} {response.content}")
    return response.json().get("token")


def _store_token(hostname, token):
    """
    Safely store the API token for the given hostname.
    """
    keyring.set_password(KEYRING_APP_NAME, hostname, token)
