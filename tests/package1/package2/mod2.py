from enum import Enum

# Enum is a not a delayed object, since it is stdlib.

assert type(Enum).__name__ == "EnumType"


class TestEnum(int, Enum):
    x = 123


assert issubclass(TestEnum, Enum)


print(__name__, end=" ")
