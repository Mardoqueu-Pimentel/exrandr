import re
from typing import Iterable


def xrandr_display_line(names: Iterable[str]):
    options = "|".join(re.escape(name) for name in names)
    return re.compile(
        r"^"
        rf"(?P<display>{options}).*?"
        rf"(connected|disconnected).*?"
        rf"(?P<resolution>\d+x\d+).*?"
        rf"(?P<displacement>(\+\d+)+)?.*?"
        r"$",
        flags=re.MULTILINE,
    )
