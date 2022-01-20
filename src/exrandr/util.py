from __future__ import annotations

import subprocess
from os import environ
from pathlib import Path

import click

import exrandr.patterns


@click.command(name="completion")
def completion_command():
    """Output shell completions."""

    def dfs(node: click.Context):
        if node is not None:
            yield from dfs(node.parent)
            yield node

    context = next(dfs(click.get_current_context()))

    completion_key = f"_{context.info_name.upper().replace('-', '_')}_COMPLETE"
    if (shell := Path(environ.get("SHELL", "/bin/bash")).name) == "bash":
        environ.setdefault(completion_key, "bash_source")
    elif shell == "zsh":
        environ.setdefault(completion_key, "zsh_source")
    elif shell == "fish":
        environ.setdefault(completion_key, "fish_source")
    else:
        raise click.UsageError(f"Unsupported {shell=!r}")

    context.command()


def find_display_names():
    xrandr_result = subprocess.run(["xrandr"], capture_output=True, text=True).stdout
    pattern = exrandr.patterns.xrandr_connected_display()
    if results := [match.groupdict()["display"] for match in pattern.finditer(xrandr_result)]:
        return results
    raise AssertionError("xrandr did not return any monitors")
