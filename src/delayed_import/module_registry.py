from .dict_tree import DictTree


class DelayedImportModuleRegistry:
    """
    Registry for tracking which modules are enabled or disabled for delayed import.
    Uses a tree structure to efficiently manage module name hierarchies.
    """

    def __init__(self):
        """Initialize the registry with empty enabled and disabled module trees."""
        self._enabled_modules = DictTree()
        self._disabled_modules = DictTree()

    def enable(self, module_name: str) -> None:
        """
        Enable delayed import for the given module and its submodules.

        Args:
            module_name (str): The name of the module to enable.
        """
        module_name_parts = tuple(module_name.split("."))
        self._enabled_modules.set_with_path(module_name_parts, DictTree())
        self._disabled_modules.del_at_path(module_name_parts, strict=False)

    def disable(self, module_name: str) -> None:
        """
        Disable delayed import for the given module and its submodules.

        Args:
            module_name (str): The name of the module to disable.
        """
        module_name_parts = tuple(module_name.split("."))
        self._disabled_modules.set_with_path(module_name_parts, DictTree())
        self._enabled_modules.del_at_path(module_name_parts, strict=False)

    def is_enabled_for_module(self, module_name: str) -> bool:
        """
        Return True if the module is enabled for delayed import, False otherwise.

        Args:
            module_name (str): The name of the module to check.

        Returns:
            bool: True if enabled, False otherwise.
        """
        module_name_parts = tuple(module_name.split("."))
        return len(self._enabled_modules.get_longest_contained_prefix(module_name_parts)) > len(
            self._disabled_modules.get_longest_contained_prefix(module_name_parts)
        )
