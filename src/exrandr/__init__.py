from importlib import metadata

from exrandr.prettyprinter import install

try:
    __version__ = metadata.version(__name__)
    install()
except metadata.PackageNotFoundError:
    __version__ = "unknown"
finally:
    del metadata
    del install
