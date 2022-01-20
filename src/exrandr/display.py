from __future__ import annotations

from collections import Counter

import attrs

from exrandr.resolution import Resolution

singletons: dict[str, Display] = {}


@attrs.define
class Display:
    name: str
    inches: float
    res: Resolution
    gamma: float
    zoom: float
    rotation: str
    primary: bool
    default_ppi: bool
    above: str | None
    below: str | None
    left: str | None
    right: str | None
    off: bool

    ppi: float | attrs.Attribute = attrs.field()

    @ppi.default
    def _(self):
        n = self.res.height * (1 + self.res.aspect_ratio**2) ** (1 / 2)
        return n / self.inches

    virt_res: Resolution | attrs.Attribute = attrs.field()

    @virt_res.default
    def _(self):
        return self.res

    def as_dict(self):
        return attrs.asdict(self)

    virt_ppi: float | attrs.Attribute = attrs.field()

    @virt_ppi.default
    def _(self):
        n = self.virt_res.height * (1 + self.virt_res.aspect_ratio**2) ** (1 / 2)
        return n / self.inches

    viewport_ratio: float | attrs.Attribute = attrs.field()

    @viewport_ratio.default
    def _(self):
        k = self.virt_res.height / self.res.height
        return k / self.zoom

    def __attrs_post_init__(self):
        m = (
            lambda: f"{self}: position (above, below, left, right) "
            f"cannot be used in conjunction with each other"
        )
        assert Counter((self.above, self.below, self.left, self.right))[None] >= 3, m()
        singletons[self.name] = self

    @property
    def xy(self):
        if self.above is not None:
            display = singletons[self.above]
            x, y = display.xy
            return x, y - display.y_size
        if self.below is not None:
            display = singletons[self.below]
            x, y = display.xy
            return x, y + display.y_size
        if self.left is not None:
            display = singletons[self.left]
            x, y = display.xy
            return x - display.x_size, y
        if self.right is not None:
            display = singletons[self.right]
            x, y = display.xy
            return x + display.x_size, y
        return 0, 0

    @property
    def x_size(self):
        k = self.res.height if self.rotation in ("left", "right") else self.res.width
        return round(k * self.viewport_ratio)

    @property
    def y_size(self):
        k = self.res.width if self.rotation in ("left", "right") else self.res.height
        return round(k * self.viewport_ratio)

    def scale(self, f: float):
        return Display(
            name=self.name,
            inches=self.inches,
            res=self.res,
            gamma=self.gamma,
            zoom=self.zoom,
            rotation=self.rotation,
            primary=self.primary,
            default_ppi=self.default_ppi,
            virt_res=Resolution(width=self.virt_res.width * f, height=self.virt_res.height * f),
            above=self.above,
            below=self.below,
            left=self.left,
            right=self.right,
            off=self.off,
        )

    def is_positioned(self):
        return (
            self.above is not None
            or self.below is not None
            or self.left is not None
            or self.right is not None
        )

    def as_xrandr_args(self):
        yield "--output"
        yield self.name

        if self.off:
            yield "-off"
            return

        yield "--mode"
        yield f"{self.res.width:.0f}x{self.res.height:.0f}"

        if self.rotation:
            yield "--rotate"
            yield self.rotation

        yield "--scale"
        yield f"{self.viewport_ratio}"

        yield "--pos"
        x, y = self.xy
        yield f"{x}x{y}"

        yield "--gamma"
        yield f"{self.gamma}"

        if self.primary:
            yield "--primary"
