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
            "There was a problem connecting to pyscript.com:\n\n" +
            f"{response.status_code} {response.reason}"
        )


def login(username, password, hostname):
    """
    Go through the process of logging the user into the pyscript.com website
    so future calls to the command line can use their token, etc...
    """
    try:
        nuauth.login(username, password, hostname)
        ok()
    except nuauth.AuthError:
        error(
            "Could not log you in."
        )


def list_projects():
    """
    List the current user's projects on pyscript.com.
    """
    response = call("get", "/projects")
    for project in response.json():
        print(f'{project["name"]} (id: {project["id"]})')
    ok()


@requires_manifest
def register_project(metadata):
    """
    Register a project on pyscript.com.
    """
    response = call("post", "/projects", payload={
        "name": metadata["app_name"],
        "description": metadata["app_description"]
    })
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
    Given a project id, delete it from pyscript.com.
    """
    call("delete", f"/projects/{project_id}")
    ok()


def host(hostname):
    """
    Set the default API hostname to the referenced instance.
    """
    nuauth.set_host(hostname)
    print(f"[bold]API points to:[/bold] {hostname}")
    ok()
