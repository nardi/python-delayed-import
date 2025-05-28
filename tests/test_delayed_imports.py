import sys  # noqa
import os
import logging
import pytest

log_level = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=log_level)

# Add tests directory to path so we can import the test packages.
sys.path.insert(0, os.path.dirname(__file__))


def test_dynamic_imports(capsys: pytest.CaptureFixture):
    import delayed_import

    with delayed_import.enable(__name__):
        from package1.mod1 import hello  # noqa
        from package1.mod1 import hello  # noqa

        # No modules should have been imported yet.
        assert capsys.readouterr() == ("", "")
        assert "package1" not in sys.modules

        import package1.package2.mod2
        from package1.package2.mod2 import x

        # Still, no modules should have been imported.
        assert capsys.readouterr() == ("", "")
        assert "package1" not in sys.modules

        from package1.mod1 import WORLD

        world = "world"
        # This should return true, but because WORLD is a wrapped object it does not.
        assert WORLD is not world

        # Still, no modules should have been imported, because `is` only acts on the wrapper.
        assert capsys.readouterr() == ("", "")

        # Now let's call the function. This should work and produce the right output.
        assert hello(WORLD) == "hello world!"

        # Now, package1 and package1.mod1 should have been imported.
        assert capsys.readouterr().out.strip() == "package1 package1.mod1"
        assert "package1" in sys.modules
        assert "package1.mod1" in sys.modules

        # package2 should not have been imported, since package1.mod1 has enabled delayed imports. However, if we disable
        # delayed imports here here and import it will be imported.
        assert "package1.package2" not in sys.modules

    import package1.package2  # noqa

    assert capsys.readouterr().out.strip() == "package1.package2"
    assert "package1.package2" in sys.modules

    # package1.package2.mod2 has not been imported, since package1.package2 has enabled delayed imports. However, if we
    # do something with the earlier imported `mod2` it will be imported.
    assert "package1.package2.mod2" not in sys.modules

    assert x + x == 246

    assert capsys.readouterr().out.strip() == "package1.package2.mod2"
    assert "package1.package2.mod2" in sys.modules
