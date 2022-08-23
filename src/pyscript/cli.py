"""The main CLI entrypoint and commands."""
import sys
import time
import webbrowser
from typing import Any, Optional

from pluggy import PluginManager

from pyscript import __version__, app, console, plugins, typer
from pyscript._generator import file_to_html, string_to_html
from pyscript.plugins import hookspecs

DEFAULT_PLUGINS = ["create", "wrap", ]


def _print_version():
    console.print(f"PyScript CLI version: {__version__}", style="bold green")


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", help="Show project version and exit."
    )
):
    """Command Line Interface for PyScript."""
    if version:
        _print_version()
        raise typer.Exit()


@app.command()
def version() -> None:
    """Show project version and exit."""
    _print_version()


class Abort(typer.Abort):
    """
    Abort with a consistent error message.
    """

    def __init__(self, msg: str, *args: Any, **kwargs: Any):
        console.print(msg, style="red")
        super().__init__(*args, **kwargs)


pm = PluginManager("pyscript-cli")

pm.add_hookspecs(hookspecs)

for modname in DEFAULT_PLUGINS:
    importspec = f"pyscript.plugins.{modname}"

    try:
        __import__(importspec)
    except ImportError as e:
        raise ImportError(
            f'Error importing plugin "{modname}": {e.args[0]}'
        ).with_traceback(e.__traceback__) from e

    else:
        mod = sys.modules[importspec]
        pm.register(mod, modname)

    loaded = pm.load_setuptools_entrypoints("pyscript-cli")

for cmd in pm.hook.pyscript_subcommand():
    plugins._add_cmd(cmd)
