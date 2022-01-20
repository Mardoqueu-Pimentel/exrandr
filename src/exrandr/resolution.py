from __future__ import annotations

import attrs
import click


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
                msg = f"{value!r} is not a valid {self.name} -> {exc!r}"
                raise click.BadParameter(msg, ctx=ctx, param=param) from exc

    aspect_ratio: float | attrs.Attribute = attrs.field()

    @aspect_ratio.default
    def _(self):
        return self.width / self.height
