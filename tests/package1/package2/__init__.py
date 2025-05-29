import delayed_import

delayed_import.enable(__name__)

# This import does not exist, but that is OK since it is not used.
from .mod2 import XYZ  # type: ignore  # noqa


class Exclaimer:
    def exclaim(self, text: str) -> str:
        return f"{text}!"


print(__name__, end=" ")
