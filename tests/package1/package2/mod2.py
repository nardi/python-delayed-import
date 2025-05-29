from enum import Enum

# Enum is a delayed object, since the parent package enabled delayed imports.

assert type(Enum).__name__ == "InheritableProxy"


class TestEnum(int, Enum):
    x = 123


print(__name__, end=" ")
