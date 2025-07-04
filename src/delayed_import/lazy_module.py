import abc
import logging
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lazy_object_proxy.simple import Proxy
else:
    from lazy_object_proxy import Proxy


logger = logging.getLogger(__name__)


class InheritableProxy(Proxy):
    """Patched version of `lazy_object_proxy.Proxy` that allows wrapping a class and then inheriting from that class."""

    def __mro_entries__(self, bases):
        """If asked for the MRO entries for the wrapper, we are likely wrapping a class. Try to get the attribute on the
        wrapped class, and if it does not exist, return the class itself (in a tuple)."""

        def _default_mro_entries(bases):
            return (self.__wrapped__,)

        mro_entries = getattr(self.__wrapped__, "__mro_entries__", _default_mro_entries)
        return mro_entries(bases)

    def __subclasscheck__(self, subclass):
        """Make sure subclass checks are run against the wrapped object(s)."""
        if type(subclass) is InheritableProxy:
            subclass = subclass.__wrapped__
        return issubclass(subclass, self.__wrapped__)  # type: ignore

    def __instancecheck__(self, instance):
        """Make sure instance checks are run against the wrapped object(s)."""
        if type(instance) is InheritableProxy:
            instance = instance.__wrapped__
        return isinstance(instance, self.__wrapped__)  # type: ignore


# Classes with ABCMeta as metaclass have a custom __subclasscheck__ implementation that directly checks whether the
# argument is a `type`. This is not the case, so we have to patch it. Luckily, there is a level of indirection so we can
# easily override the function responsible.
try:
    _orig_abc_subclasscheck = abc._abc_subclasscheck  # type: ignore

    def _abc_subclasscheck(cls, subclass):
        if type(subclass) is InheritableProxy:
            return _abc_subclasscheck(cls, subclass.__wrapped__)
        return _orig_abc_subclasscheck(cls, subclass)

    abc._abc_subclasscheck = _abc_subclasscheck  # type: ignore
except ImportError:
    # If the _abc_subclasscheck function does not exist, we also don't have to patch it.
    pass


class LazyModule(ModuleType):
    """
    Wraps a module object, allowing lazy access to a subset of its attributes.
    """

    __slots__ = ["_module_name", "_module_proxy", "_lazy_submodules", "_lazy_attrs"]

    def __init__(
        self, module_name: str, module_proxy: Proxy, lazy_submodules: tuple[str, ...], lazy_attrs: tuple[str, ...]
    ):
        """
        Initialize a LazyModule instance.

        The attributes named in `lazy_attrs` will be returned as proxy objects, that resolve the import of the module
        when used. If a submodule is lazily imported, the submodule names can be provided in `lazy_modules`, and these
        will be wrapped in a LazyModule object as well.

        Args:
            module_name (str): The name of the module. module_proxy (Proxy): Proxy for the real module import.
            lazy_submodules (tuple[str, ...]): Submodules to be lazily imported. lazy_attrs (tuple[str, ...]):
            Attributes to be lazily imported.
        """
        self._module_name = module_name
        self._module_proxy = module_proxy
        self._lazy_submodules = lazy_submodules
        self._lazy_attrs = lazy_attrs

    def __getattribute__(self, name: str) -> Any:
        """
        Custom attribute access for lazy loading of submodules and attributes.
        Args:
            name (str): The attribute name to access.
        Returns:
            Any: The attribute value, possibly a proxy for lazy loading.
        """
        if name in LazyModule.__slots__:
            return super().__getattribute__(name)

        logger.debug(f"getattribute {name = } on lazy module {self._module_name}")

        def lazy_getattr():
            return getattr(self._module_proxy, name)

        if name in self._lazy_submodules:
            return LazyModule(name, Proxy(lazy_getattr), self._lazy_submodules[1:], self._lazy_attrs)

        if name in self._lazy_attrs:
            # The wrapped attribute might be a class, so return an InheritableProxy.
            return InheritableProxy(lazy_getattr)

        return getattr(self._module_proxy, name)
