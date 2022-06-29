#!/usr/bin/env python3
from __future__ import annotations

import itertools
import math
import os
import re

import attr
import click
from attrs import define


@define
class Display:
    name: str
    physical_diagonal: float

    height: float
    aspect_ratio: float
    viewport_height: float
    viewport_aspect_ratio: float

    zoom: float

    gamma: float
    rotation: str
    primary: bool

    def __attrs_post_init__(self):
        if self.rotation in ("left", "right"):
            self.viewport_height = self.viewport_width
            self.viewport_aspect_ratio = 1 / self.viewport_aspect_ratio

    @property
    def width(self):
        return self.height * self.aspect_ratio

    @property
    def viewport_width(self):
        return self.viewport_height * self.viewport_aspect_ratio

    @property
    def ppi(self):
        n = self.height * (1 + self.aspect_ratio ** 2) ** (1 / 2)
        return n / self.physical_diagonal

    @property
    def viewport_ratio(self):
        return self.zoomed_viewport_height / (self.width if self.rotation else self.height)

    @property
    def zoomed_viewport_height(self):
        return self.viewport_height / self.zoom

    @property
    def zoomed_viewport_width(self):
        return self.viewport_width / self.zoom

    @classmethod
    def from_str(cls, s: str):
        def unpack_and_make(
            name: str, inches: str, res: str, zoom: str = "1.0",
            gamma: str = "1.0",
            rotation: str | None = None, primary: str | None = None
        ):
            width, height = map(float, res.split("x"))
            return Display(
                name=name,
                physical_diagonal=float(inches),
                height=height,
                aspect_ratio=width / height,
                viewport_height=height,
                viewport_aspect_ratio=width / height,
                zoom=float(zoom),
                gamma=float(gamma),
                rotation=rotation,
                primary=eval(primary) if primary else False,
            )

        items = [arg.split("=") for arg in re.split(r", +| +", s)]
        kwargs = {k: v for k, v in items}
        return unpack_and_make(**kwargs)

    def ppi_scale(self, ppi: float):
        height = ppi * self.physical_diagonal / (1 + self.aspect_ratio ** 2) ** (1 / 2)
        return attr.evolve(self, viewport_height=self.viewport_height * (height / self.height))

    def ui_scale(self, scale: float):
        return attr.evolve(self, viewport_height=self.viewport_height * scale)

    def as_dict(self):
        return attr.asdict(self)

    def as_xrandr_args(self, position: int):
        yield "--output"
        yield self.name
        yield "--mode"
        yield f"{self.width:.0f}x{self.height:.0f}"
        if self.rotation:
            yield "--rotate"
            yield self.rotation
        yield "--scale"
        yield f"{self.viewport_ratio}"
        yield "--pos"
        yield f"{position}x0"
        yield "--gamma"
        yield f"{self.gamma}"
        if self.primary:
            yield "--primary"

    def __repr__(self, properties=()):
        properties = properties or [
            k for
            k, v in self.__class__.__dict__.items()
            if isinstance(v, property)
        ]

        d = self.as_dict()
        keys = itertools.chain(d.items(), [(k, getattr(self, k)) for k in properties])

        if len(attributes := ", ".join(f"{k}={v}" for k, v in keys)) >= 80:
            attributes = attributes.replace(", ", "\n\t")

        if len(result := f"{self.__class__.__name__}({attributes})") >= 80:
            result = f"{self.__class__.__name__}(\n\t{attributes}\n)\n"

        return result


def int_or_float(x: str):
    try:
        return int(x)
    except Exception:
        return float(x)


@click.command()
@click.option("--scale", default=1, type=int)
@click.option(
    "--display",
    "displays",
    required=True,
    multiple=True,
    help="""
    Format: 
        S -> "name=<str>" "inches=<int>" "res=<3840>x<2160>" [OPT...]
        OPT -> ZOOM | GAMMA | ROTATION | PRIMARY
        ZOOM -> "zoom=<float>"
        GAMMA -> "gamma=<float>"
        ROTATION -> "rotation=<float>"
        PRIMARY -> "primary=True"
    """,
    callback=lambda _, __, xs: [Display.from_str(x) for x in xs],
)
@click.option("--ppi", type=int_or_float, default="1")
@click.option("--apply", is_flag=True, default=False)
@click.option("-v", "--verbose", is_flag=True, default=False)
def main(scale: int, displays: list[Display], ppi: float | int, apply: bool, verbose: bool):
    assert ppi is None or ppi > 0

    cmd = ["xrandr"]
    position = 0

    if isinstance(ppi, int):
        ppi = displays[ppi - 1].ppi

    displays = [display.ui_scale(scale).ppi_scale(ppi) for display in displays]

    for display in displays:
        if verbose:
            print(display)
        cmd.append(" ".join(display.as_xrandr_args(position)))
        position += round(display.zoomed_viewport_width)

    result = " \\\n\t".join(cmd) + ("" if apply else " | :")
    click.echo(result)

    if apply:
        os.system(result)


def run():
    main()


if __name__ == "__main__":
    run()
