#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess

import click
from prettyprinter import cpprint

import exrandr.commands
import exrandr.patterns
from exrandr import util
from exrandr.display import Display
from exrandr.resolution import Resolution
from exrandr.util import find_display_names


@click.group(chain=True)
@click.option(
    "--scale",
    "-s",
    type=float,
    default=1.0,
    show_default=True,
    help="The desktop Scale to use. 1 for 100%, 2 for 200%, 3 for 300%. Only Gnome is supported.",
)
@click.option(
    "--ppi",
    "-p",
    type=float,
    default=None,
    show_default=True,
    help="Force this ppi instead of choosing the lowest one of a monitor. If 0 no ppi scaling will be made.",
)
@click.option(
    "--apply",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Call xrandr.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output.",
)
def main(scale: float, ppi: float | None, apply: bool, verbose: bool):
    pass


main.add_command(util.completion_command)  # type: ignore


@main.command("display", help="Configure a xrandr display.")
@click.option(
    "--name",
    "-n",
    type=click.Choice(find_display_names()),
    required=True,
    help="Name of the monitor on xrandr.",
)
@click.option(
    "--inches",
    "-i",
    type=float,
    required=True,
    help="The size of the diagonal of the monitor in inches.",
)
@click.option(
    "--resolution", "-r", type=Resolution.ParamType(), help="The true resolution of the monitor."
)
@click.option(
    "--gamma", "-g", type=float, default=1.0, show_default=True, help="The gamma of the monitor."
)
@click.option(
    "--zoom", "-z", type=float, default=1.0, show_default=True, help="The zoom you want to apply."
)
@click.option(
    "--rotation",
    "-o",
    type=click.Choice(["normal", "inverted", "left", "right"]),
    default="normal",
    show_default=True,
    help="If the monitor should be rotated.",
)
@click.option(
    "--primary",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether the monitor is primary.",
)
@click.option(
    "--default-ppi",
    is_flag=True,
    default=False,
    show_default=True,
    help="Mark this monitor as the default ppi for ppi scaling.",
)
@click.option(
    "--above",
    type=str,
    default=None,
    show_default=True,
    help="The monitor which this monitor is above.",
)
@click.option(
    "--below",
    type=str,
    default=None,
    show_default=True,
    help="The monitor which this monitor is below.",
)
@click.option(
    "--left",
    type=str,
    default=None,
    show_default=True,
    help="The monitor which this monitor is left",
)
@click.option(
    "--right",
    type=str,
    default=None,
    show_default=True,
    help="The monitor which this monitor is right",
)
@click.option(
    "--off", is_flag=True, default=False, show_default=True, help="Turn off this monitor."
)
def process_display(
    name: str,
    inches: float,
    resolution: Resolution,
    gamma: float,
    zoom: float,
    rotation: str | None,
    primary: bool,
    default_ppi: bool,
    above: str,
    below: str,
    left: str,
    right: str,
    off: bool,
):
    return Display(
        name=name,
        inches=inches,
        res=resolution,
        gamma=gamma,
        zoom=zoom,
        rotation=rotation,
        primary=primary,
        default_ppi=default_ppi,
        above=above,
        below=below,
        left=left,
        right=right,
        off=off,
    )


@main.result_callback()
def process_displays(
    displays: list[Display], scale: float, ppi: float | None, apply: float, verbose: bool
):
    displays_aspect_ratios = {d.res.aspect_ratio for d in displays}
    primary_displays = [d for d in displays if d.primary]
    default_ppi_displays = [d for d in displays if d.default_ppi]

    assert len(displays_aspect_ratios) == 1, "All displays must have the same aspect ratio"
    assert len(primary_displays) == 1, "One display must be primary"
    assert len(default_ppi_displays) <= 1, "At most one display must be default_ppi"

    m = (
        lambda: f"{displays[0]=}: the first display should not have a "
        f"position (above, below, left, right)"
    )
    assert not displays[0].is_positioned(), m()
    for display in displays[1:]:
        m = (
            lambda: f"{display=}: all subsequent displays after the first must have a "
            f"position (above, below, left, right)"
        )
        assert display.is_positioned(), m()
        x, y = display.xy
        m = lambda: f"{display.xy=}: display position must be positive"
        assert x >= 0 and y >= 0, m()

    int_scale = int(scale)
    if scale == int_scale:
        cmd = exrandr.commands.gsettings_set_xsettings(int_scale=int_scale)
        click.echo(f"$ {cmd}")
        os.system(cmd)
        cmd = exrandr.commands.gsettings_set_interface_scaling_factor(int_scale=int_scale)
        click.echo(f"$ {cmd}")
        os.system(cmd)
    displays = [d.scale(scale) for d in displays]

    if ppi is None:
        if default_ppi_displays:
            display = default_ppi_displays[0]
            ppi = display.ppi
            click.echo(f"ppi scale: using {ppi=} of {display=}")
        else:
            display = min(displays, key=lambda d: d.ppi)
            ppi = display.ppi
            click.echo(f"ppi scale: default to minimum {ppi=} of {display=}")
        displays = [d.scale(ppi / d.ppi) for d in displays]
    elif ppi > 0.0:
        click.echo(f"ppi scale: using {ppi=}")
        displays = [d.scale(ppi / d.ppi) for d in displays]

    cmd = ["xrandr"]
    for display in displays:
        if verbose:
            cpprint(display)
        cmd.append(" ".join(display.as_xrandr_args()))

    result = " \\\n\t".join(cmd) + ("" if apply else " | :")
    click.echo(f"$ {result}")

    if apply:
        os.system(result)
        xrandr_result = subprocess.run(["xrandr"], capture_output=True, text=True).stdout
        pattern = exrandr.patterns.xrandr_display_line(d.name for d in displays)
        if results := {
            (d := match.groupdict()).pop("display"): d for match in pattern.finditer(xrandr_result)
        }:
            cpprint({"displays": results})


def run():
    main()


if __name__ == "__main__":
    run()
