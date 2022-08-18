import requests
import typer
import toml
from pathlib import Path
from pyscript import nuauth
from rich import print


def error(message):
    """
    Uniformly displays an error message and exits(1).
    """
    print(f"[bold red]Error:[/bold red] {message}")
    raise typer.Exit(1)


def requires_manifest(func):
    """
    Decorator to ensure the command is run in a directory containing a
    project's manifest.toml file.
    """

    def inner(*args, **kwargs):
        manifest = Path("manifest.toml")
        if not manifest.is_file():
            error(
                "Cannot find a manifest.toml in the current directory.\n"
                "Please [bold]change into the project's directory[/bold] "
                "for this command to work."
            )
        with manifest.open("r") as f:
            metadata = toml.load(f)
        return func(metadata, *args, **kwargs)

    return inner


def ok():
    """
    Simply prints "OK" in green to the console.
    """
    print("[green]OK[/green]")


def call(method, path, payload=None):
    """
    Wraps calling the API.

    Will always exit with a helpful error message if anything goes wrong (a non
    2xx response status).

    The payload is a Python object that's JSON serializable.
    """
    method = method.lower()
    token = nuauth.get_token()
    domain = nuauth.get_host()
    headers = {
        "Authorization": f"Bearer {token}",
    }
    # Currently the smallest requests based call possible.
    url = f"{domain}{path}"
    if method in ("post", "put"):
        response = getattr(requests, method)(url, json=payload, headers=headers)
    else:
        response = getattr(requests, method)(url, headers=headers)
    if 200 <= response.status_code < 300:
        return response
    else:
        error(
            f"There was a problem connecting to {domain}:\n\n"
            + f"{response.status_code} {response.reason}"
        )


def login(username, password, hostname):
    """
    Go through the process of logging the user into the API host
    so future calls to the command line can use their token, etc...
    """
    if not hostname:
        hostname = nuauth.get_host()
    try:
        nuauth.login(username, password, hostname)
        ok()
    except nuauth.AuthError:
        error("Could not log you in.")


def logout():
    """
    Clear the user's token.
    """
    nuauth.logout(nuauth.get_host())
    ok()


def list_projects():
    """
    List the current user's projects.
    """
    response = call("get", "/projects")
    for project in response.json():
        print(f'{project["name"]} (id: {project["id"]})')
    ok()


@requires_manifest
def register_project(metadata):
    """
    Register a project with the API.
    """
    response = call(
        "post",
        "/projects",
        payload={
            "name": metadata["app_name"],
            "description": metadata["app_description"],
        },
    )
    ok()


@requires_manifest
def push_project(metadata):
    """
    Push files to the current project.
    """
    # TODO: This needs working out.
    ok()


@requires_manifest
def delete_project(metadata):
    """
    Delete the current project.
    """
    delete_project_by_id(metadata["id"])


def delete_project_by_id(project_id):
    """
    Given a project id, delete it.
    """
    call("delete", f"/projects/{project_id}")
    ok()


def host(hostname=None):
    """
    Set or return the default API hostname to the referenced instance.
    """
    if hostname:
        nuauth.set_host(hostname)
    else:
        hostname = nuauth.get_host()
    print(f"[bold]API points to:[/bold] {hostname}")
    ok()
