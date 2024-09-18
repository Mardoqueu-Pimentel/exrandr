#!/usr/bin/env python3
from __future__ import annotations

import os
from collections import Counter

import attrs
import click
from prettyprinter import cpprint
import exrandr.cmd_factory


@attrs.define
class Resolution:
    width: float
    height: float

    class ParamType(click.ParamType):
        name = "Resolution"

        def convert(
            self, value: Resolution | str, param: click.Parameter | None, ctx: click.Context | None
        ) -> Resolution:
            if isinstance(value, Resolution):
                return value

            try:
                width, sep, height = value.partition("x")
                if sep != "x":
                    raise ValueError("'x' separator not found")
                return Resolution(width=float(width), height=float(height))
            except ValueError as exc:
                self.fail(f"{value!r} is not a valid {self.name} -> {exc!r}", param, ctx)
                raise

    aspect_ratio: float = attrs.field()

    @aspect_ratio.default
    def _(self):
        return self.width / self.height


@attrs.define
class Display:
    name: str
    inches: float
    viewport: Resolution
    gamma: float
    zoom: float
    rotation: str
    primary: bool
    default_ppi: bool

    ppi: float = attrs.field()

    @ppi.default
    def _(self):
        n = self.viewport.height * (1 + self.viewport.aspect_ratio ** 2) ** (1 / 2)
        return n / self.inches

    vr: Resolution = attrs.field()

    @vr.default
    def _(self):
        return self.viewport

    def as_dict(self):
        return attrs.asdict(self)

    vppi: float = attrs.field()

    @vppi.default
    def _(self):
        n = self.vr.height * (1 + self.vr.aspect_ratio ** 2) ** (1 / 2)
        return n / self.inches

    zoomed_vr_viewport_ratio: float = attrs.field()

    @zoomed_vr_viewport_ratio.default
    def _(self):
        k = self.vr.height / self.viewport.height
        return k / self.zoom

    def scale(self, f: float):
        return Display(
            name=self.name,
            inches=self.inches,
            viewport=self.viewport,
            gamma=self.gamma,
            zoom=self.zoom,
            rotation=self.rotation,
            primary=self.primary,
            default_ppi=self.default_ppi,
            vr=Resolution(width=self.vr.width * f, height=self.vr.height * f),
        )

    def as_xrandr_args(self, position: int):
        yield "--output"
        yield self.name
        yield "--mode"
        yield f"{self.viewport.width:.0f}x{self.viewport.height:.0f}"
        if self.rotation:
            yield "--rotate"
            yield self.rotation
        yield "--scale"
        yield f"{self.zoomed_vr_viewport_ratio}"
        yield "--pos"
        yield f"{position}x0"
        yield "--gamma"
        yield f"{self.gamma}"
        if self.primary:
            yield "--primary"


@click.group(chain=True)
@click.option("--scale", "-s", type=float, default=1.0, show_default=True)
@click.option("--ppi", "-p", type=float, default=None, show_default=True)
@click.option("--apply", "-a", is_flag=True, default=False, show_default=True)
@click.option("--verbose", "-v", is_flag=True, default=False, show_default=True)
def main(scale: float, ppi: float | None, apply: bool, verbose: bool):
    pass


@main.command("display")
@click.option("--name", "-n", type=str, required=True)
@click.option("--inches", "-i", type=float, required=True)
@click.option("--resolution", "-r", type=Resolution.ParamType())
@click.option("--gamma", "-g", type=float, default=1.0, show_default=True)
@click.option("--zoom", "-z", type=float, default=1.0, show_default=True)
@click.option("--rotation", "-o", type=str, default="", show_default=True)
@click.option("--primary", "-p", is_flag=True, default=False, show_default=True)
@click.option("--default-ppi", is_flag=True, default=False, show_default=True)
def process_display(
    name: str,
    inches: float,
    resolution: Resolution,
    gamma: float,
    zoom: float,
    rotation: str | None,
    primary: bool,
    default_ppi: bool,
):
    return Display(
        name=name,
        inches=inches,
        viewport=resolution,
        gamma=gamma,
        zoom=zoom,
        rotation=rotation,
        primary=primary,
        default_ppi=default_ppi,
    )


@main.result_callback()
def process_displays(
    displays: list[Display], scale: float, ppi: float | None, apply: float, verbose: bool
):
    displays_aspect_ratios = {d.viewport.aspect_ratio for d in displays}
    primary_displays = [d for d in displays if d.primary]
    default_ppi_displays = [d for d in displays if d.default_ppi]

    assert len(displays_aspect_ratios) == 1, "All displays must have the same aspect ratio"
    assert len(primary_displays) == 1, "One display must be primary"
    assert len(default_ppi_displays) <= 1, "At most one display must be default_ppi"

    int_scale = int(scale)
    if scale == int_scale:
        cmd = exrandr.cmd_factory.gsettings_set_xsettings(int_scale=int_scale)
        click.echo(f"$ {cmd}")
        os.system(cmd)
        cmd = exrandr.cmd_factory.gsettings_set_interface_scaling_factor(int_scale=int_scale)
        click.echo(f"$ {cmd}")
        os.system(cmd)

    displays = [d.scale(scale) for d in displays]

    if ppi is None:
        ppi = default_ppi_displays and default_ppi_displays[0].ppi or min(d.ppi for d in displays)
    if ppi > 0.0:
        displays = [d.scale(ppi / d.ppi) for d in displays]

    cmd = ["xrandr"]
    position = 0
    for display in displays:
        if verbose:
            cpprint(display)
        cmd.append(" ".join(display.as_xrandr_args(position)))
        position += round(
            (display.viewport.height if display.rotation else display.viewport.width)
            * display.zoomed_vr_viewport_ratio
        )

    result = " \\\n\t".join(cmd) + ("" if apply else " | :")
    click.echo(result)

    if apply:
        os.system(result)


def run():
    main()


if __name__ == "__main__":
    run()
