import logging
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lazy_object_proxy.simple import Proxy
else:
    from lazy_object_proxy import Proxy


logger = logging.getLogger(__name__)


class LazyModule(ModuleType):
    """
    Wraps a module object, allowing lazy access to a subset of its attributes.
    """

    __slots__ = ["_module_name", "_module_proxy", "_lazy_submodules", "_lazy_attrs"]

    def __init__(
        self, module_name: str, module_proxy: "Proxy", lazy_submodules: tuple[str, ...], lazy_attrs: tuple[str, ...]
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
            return Proxy(lazy_getattr)

        return getattr(self._module_proxy, name)
