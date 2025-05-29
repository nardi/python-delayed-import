import delayed_import

delayed_import.enable(__name__)

from .package2 import Exclaimer  # noqa

WORLD = "world"


class HelloExclaimer(Exclaimer):
    def hello(self, name: str) -> str:
        return self.exclaim(f"hello {name}")


print(__name__, end=" ")
