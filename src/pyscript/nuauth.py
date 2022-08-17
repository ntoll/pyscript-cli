"""
Nucleus authentication utilities.

login - log into the Nucleus platform.
get_token - once logged in, get the token for making API calls.
logout - log out of the Nucleus platform (clear the token).

Based upon code found in the conda-cli repos.
"""


class AuthError(Exception):
    """
    Raised when the user is unable to login to the API.
    """
    pass


def login(username, password, hostname):
    """
    Go through the process of logging the user into the pyscript.com website
    so future calls to the command line can use their token, etc...
    """
    token = _interactive_get_token()
    _store_token(token, username, hostname)


def _interactive_get_token():
    pass


def _store_token(username, hostname):
    pass
