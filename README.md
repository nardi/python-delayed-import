# delayed-import

`delayed-import` is a Python library that lets you selectively change the behavior of import statements to delay the actual import action. It can be enabled/disabled per module and should work mostly transparently otherwise.

## Installation

Install `delayed-import` with any Python package manager.

## Motivation

Suppose you have a module `mod1` that imports a library function, defines a function of its own, and optionally calls both on some user input when executed as a script:

```python
import sys

from package1.package2 import func1

def func2(text: str) -> str:
    return f"func2: {text}"

if __name__ == "__main__":
    user_input = sys.argv[1]
    print(func1(user_input))
    print(func2(user_input))
```

When executing this as a script, it works as expected. But maybe another module would like to import `mod1` as a library and only call `func2`. To do so, `func1` must first be imported, which may depending on the structure of the containing packages entail a lot of extra work.

To make this module lighter to import, you could move the import of `func1` to inside the `if __name__ == "__main__":` block. But this is not always an easy refactor and might lead to many repeated import statements. This library offers an alternative, by making the import **delayed**: this means that when you write the import statement, the name `func1` is assigned a wrapper object that will resolve to the actual `func1` when it is used. The [`lazy-object-proxy`](https://github.com/ionelmc/python-lazy-object-proxy) package is used for this.

The modified example would look like this:

```python
import delayed_import

# Enable delayed imports in the current module and all submodules.
delayed_import.enable(__name__)

import sys

from package1.package2 import func1

def func2(text: str) -> str:
    return f"func2: {text}"

if __name__ == "__main__":
    user_input = sys.argv[1]
    print(func1(user_input))
    print(func2(user_input))
```

This code will function the same, except that the imports of `package1` and `package1.package2` are **delayed** until the moment they are used, when `func1` is called. That means that if this file is imported as a module, they will not be imported at all. (Actually, the import of `sys` is similarly delayed, though it is likely already imported by this point.) It would be roughly equivalent to the following:

```python
def func2(text: str) -> str:
    return f"func2: {text}"

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1]
    from package1.package2 import func1
    print(func1(user_input))
    print(func2(user_input))
```

## Usage

To use in a module, import the library and call `enable` with the module name:

```python
import delayed_import

delayed_import.enable(__name__)
```

This makes all import statements that are executed in that module from that point on delayed. It is possible to later disable delayed imports by calling `disable` with the module name.

```python
import delayed_import

delayed_import.enable(__name__)

# ...delayed imports...

delayed_import.disable(__name__)

# ...regular imports...
```

A block of imports can also be delayed by using `enable` as a context manager.

```python
import delayed_import

with delayed_import.enable(__name__):
    # ...delayed imports...

# ...regular imports...
```

When enabling delayed imports, this will also affect submodules, allowing you to enable/disable them for entire code trees at once. You can mix enabling and disabling, i.e. if `a` enables them, and `a.b` disables them, then in `a.c` they will be enabled and in `a.b.d` they will be disabled.

It is possible to enable delayed imports for any module, not just for the current one. However, since delayed imported objects are not equivalent to their non-delayed equivalents, it might be necessary to adjust the importing code to take this difference into account.

## Caveats

The main caveats have to do with the wrapping of the imported objects. This means that the imported object is not actually the same object as the one in the imported module. However, `lazy-object-proxy` wraps the object pretty thouroughly, so this is rarely observable. The biggest difference is that referential equality will be broken. So the following will fail with an `AssertionError`:

```python
import delayed_import

delayed_import.enable(__name__)

# x1 wraps x, to delay the import.
from package1 import x as x1

delayed_import.disable(__name__)

# x2 is the real x, since delayed imports are disabled.
from package1 import x as x2

# This will work...
assert x1 == x2

# ...but this will fail!
assert x1 is x2
```

Moreover, because a new wrapper is created for every import statement, importing the same object twice will also not compare equal with `is`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgements

README template from [https://www.makeareadme.com]().