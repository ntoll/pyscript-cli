from pathlib import Path
from typing import Optional

import jinja2
import toml
import datetime

_env = jinja2.Environment(loader=jinja2.PackageLoader("pyscript"))


def string_to_html(input_str: str, title: str, output_path: Path) -> None:
    """Write a Python script string to an HTML file template."""
    template = _env.get_template("basic.html")
    with output_path.open("w") as fp:
        fp.write(template.render(code=input_str, title=title))


def file_to_html(input_path: Path, title: str, output_path: Optional[Path]) -> None:
    """Write a Python script string to an HTML file template."""
    output_path = output_path or input_path.with_suffix(".html")
    with input_path.open("r") as fp:
        string_to_html(fp.read(), title, output_path)


def new_project(
    app_name: str,
    app_description: str,
    author_name: str,
    author_email: str,
) -> None:
    """
    New files created:

    manifest.toml - project metadata
    index.html - a "Hello world" start page for the project.

    TODO: more files to add to the core project start state.
    """
    version = f"{datetime.date.today().year}.1.1"
    created_on = datetime.datetime.now()
    context = {k: v for k, v in locals().items() if not k.startswith("__")}
    app_dir = Path(".") / app_name
    app_dir.mkdir()
    manifest_file = app_dir / "manifest.toml"
    toml.dump(context, manifest_file.open("w", encoding="utf-8"))
    index_file = app_dir / "index.html"
    string_to_html('print("Hello, world!")', app_name, index_file)
