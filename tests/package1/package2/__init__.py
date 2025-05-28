import delayed_import

delayed_import.enable(__name__)

from .mod2 import x  # noqa

print(__name__, end=" ")
