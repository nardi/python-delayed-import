import logging
import os
import sys  # noqa
from abc import ABC
from enum import Enum

import pytest

log_level = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=log_level)

# Add tests directory to path so we can import the test packages.
sys.path.insert(0, os.path.dirname(__file__))


def test_dynamic_imports(capsys: pytest.CaptureFixture):
    import delayed_import

    with delayed_import.enable(__name__):
        from package1.mod1 import HelloExclaimer  # noqa
        from package1.mod1 import HelloExclaimer  # noqa

        # No modules should have been imported yet.
        assert capsys.readouterr() == ("", "")
        assert "package1" not in sys.modules

        import package1.package2.mod2  # noqa
        from package1.package2.mod2 import TestEnum

        # Still, no modules should have been imported.
        assert capsys.readouterr() == ("", "")
        assert "package1" not in sys.modules

        from package1.mod1 import WORLD

    # Delayed imports are now disabled, however since we do not import anything anymore the previously imported objects
    # are still delayed.
    assert capsys.readouterr() == ("", "")

    world = "world"
    # This should return true, but because WORLD is a wrapped object it does not.
    assert WORLD is not world

    # Still, no modules should have been imported, because `is` only acts on the wrapper.
    assert capsys.readouterr() == ("", "")

    # Now let's create the imported class. This should work and produce the right output.
    ex = HelloExclaimer()
    assert ex.hello(WORLD) == "hello world!"

    # Now, package1, package1.package2 and package1.mod1 should have been imported.
    assert capsys.readouterr().out.strip() == "package1 package1.package2 package1.mod1"
    assert "package1" in sys.modules
    assert "package1.package2" in sys.modules
    assert "package1.mod1" in sys.modules

    # package1.package2.mod2 has not been imported, since package1.package2 has enabled delayed imports. However, if we
    # do something with the earlier imported `mod2` it will be imported.
    assert "package1.package2.mod2" not in sys.modules

    assert TestEnum.x + TestEnum.x == 246
    assert isinstance(TestEnum.x, TestEnum)
    assert issubclass(TestEnum, Enum)

    assert capsys.readouterr().out.strip() == "package1.package2.mod2"
    assert "package1.package2.mod2" in sys.modules

    class ABCTest(ABC):
        """This class only exists to test issubclass checks against ABC classes don't crash."""

        pass

    assert not issubclass(TestEnum, ABCTest)
