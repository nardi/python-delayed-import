import builtins
import logging
import sys
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lazy_object_proxy.simple import Proxy
else:
    from lazy_object_proxy import Proxy

from .lazy_module import LazyModule
from .module_registry import DelayedImportModuleRegistry

logger = logging.getLogger(__name__)

_original_import = builtins.__import__
"""Reference to the original built-in __import__ function."""

_module_registry = DelayedImportModuleRegistry()
"""Registry instance for managing enabled/disabled modules for delayed import."""


@contextmanager
def _disable_on_exit(module_name: str) -> Generator[None]:
    """
    Returns a context manager that disables delayed imports for the given module and its submodules.
    Args:
        module_name (str): The name of the module to disable delayed import for.
    """
    yield
    _module_registry.disable(module_name)


def enable(module_name: str) -> AbstractContextManager[None]:
    """
    Enable delayed imports for the given module and its submodules. Can be used as a context manager to temporarily
    enable delayed imports.
    Args:
        module_name (str): The name of the module to enable delayed import for.
    """
    _module_registry.enable(module_name)
    # Return a context manager that will disable the just enabled module on exit.
    return _disable_on_exit(module_name)


def disable(module_name: str) -> None:
    """
    Disable delayed imports for the given module and its submodules.
    Args:
        module_name (str): The name of the module to disable delayed import for.
    """
    _module_registry.disable(module_name)


def __import__(
    name: str, globals: dict | None = None, locals: dict | None = None, fromlist: tuple[str, ...] = (), level: int = 0
) -> ModuleType:
    """
    Custom import function that supports delayed imports for enabled modules.
    Args:
        name (str): The name of the module to import.
        globals (dict | None): The globals dictionary from the calling context.
        locals (dict | None): The locals dictionary from the calling context.
        fromlist (tuple[str, ...]): Names to import from the module.
        level (int): The level of relative import.
    Returns:
        ModuleType: The imported module, possibly wrapped for lazy loading.
    """
    caller_name = (globals or {}).get("__name__")
    logger.debug(f"__import__ called from {caller_name = } with {name = }, {fromlist = }, {level = }")

    module_name, *lazy_submodules = name.split(".")
    # We disable delayed import of stdlib modules, since these are so common they generally will need to be imported
    # sooner or later anyway. Not importing them normally can cause problems since they tend to reply more heavily on
    # (C)Python internals.
    is_stdlib = module_name in sys.stdlib_module_names

    is_enabled = not is_stdlib and caller_name is not None and _module_registry.is_enabled_for_module(caller_name)
    if not is_enabled:
        return _original_import(name, globals, locals, fromlist, level)

    def real_import():
        """
        Perform the actual import and log the import event.
        Returns:
            ModuleType: The imported module.
        """
        new_import = module_name not in sys.modules
        if new_import:
            logger.debug(f"Doing import of module {module_name}")
        module = _original_import(name, globals, locals, fromlist, level)
        if new_import:
            logger.debug(f"Imported {module.__name__ = }")
        return module

    # If names are mentioned in "fromlist", we want to import these lazily.
    lazy_attrs = tuple(fromlist or [])

    return LazyModule(module_name, Proxy(real_import), tuple(lazy_submodules), lazy_attrs)


builtins.__import__ = __import__
"""Override the built-in __import__ function with the custom delayed import version."""
