#!/usr/bin/env python3

import click
from attrs import define

default_zoom = "1.0"
default_gamma = "1.0"
default_rotation = ""
default_primary = ""

default_values = [default_zoom, default_gamma, default_rotation, default_primary]


@define
class Display:
    name: str
    width: int
    height: int
    zoom: float
    gamma: float
    rotation: str
    primary: bool

    @classmethod
    def from_str(cls, s: str):
        args = s.split(",")

        assert len(args) >= (k := 2)
        if (n := len(args)) != 6:
            args.extend(default_values[n - k :])

        name, resolution, zoom, gamma, rotation, primary = args
        width, height = resolution.split("x")

        return Display(
            name,
            int(width),
            int(height),
            float(zoom or default_zoom),
            float(gamma or default_gamma),
            rotation or default_rotation,
            (primary or default_primary).lower() == "p",
        )


@click.command()
@click.option("--scale", default=1, type=int)
@click.option(
    "--display",
    "displays",
    required=True,
    multiple=True,
    help="Format: name,resolution,zoom,gamma,rotation,primary",
    callback=lambda _, __, xs: [Display.from_str(x) for x in xs],
)
def main(scale: int, displays: list[Display]):
    cmd = ["xrandr"]
    width_sum = 0.0
    for display in displays:
        partial = [
            "--output",
            display.name,
            "--mode",
            f"{display.width}x{display.height}",
            "--scale",
            str(xrandr_scale := scale / display.zoom),
            "--pos",
            f"{width_sum:.0f}x0",
            "--gamma",
            str(display.gamma),
        ]

        if display.rotation:
            display.width, display.height = display.height, display.width

            partial.append("--rotation")
            partial.append(display.rotation)

        width_sum += display.width * xrandr_scale

        if display.primary:
            partial.append("--primary")

        cmd.append(" ".join([str(x) for x in partial]))

    result = " \\\n\t".join(cmd) + " | :"

    print(result)


def run():
    main()


if __name__ == "__main__":
    run()
