import delayed_import

delayed_import.enable(__name__)

from . import package2  # noqa

WORLD = "world"


def hello(name: str) -> str:
    return f"hello {name}!"


print(__name__, end=" ")
