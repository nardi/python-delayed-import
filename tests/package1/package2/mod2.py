from enum import Enum

# Enum is a delayed object, since the parent package enabled delayed imports.

assert type(Enum).__name__ == "InheritableProxy"


class TestEnum(int, Enum):
    x = 123


assert issubclass(TestEnum, Enum)
assert issubclass(TestEnum, Enum.__wrapped__)  # type: ignore


print(__name__, end=" ")
