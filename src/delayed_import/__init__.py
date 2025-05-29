from .core import Proxy, disable, enable

__all__ = ["disable", "enable"]


def get_version() -> str:
    import importlib.metadata

    try:
        return importlib.metadata.version(__name__)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


__version__ = Proxy(get_version)
"""Package version, but with delayed evaluation (of course!)."""
