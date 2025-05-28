from collections import defaultdict
from typing import Any


class DictTree(defaultdict):
    """
    A tree-like dictionary structure for storing hierarchical data, such as module names split by dot notation.
    Inherits from collections.defaultdict and recursively creates DictTree nodes.
    """

    def __init__(self):
        """Initialize a DictTree node."""
        return super().__init__(DictTree)

    def get_from_path(self, path: tuple) -> Any:
        """
        Retrieve a value from the tree using a tuple path.
        Args:
            path (tuple): The path to traverse.
        Returns:
            Any: The value at the specified path.
        Raises:
            ValueError: If the path is empty.
        """
        if not path:
            raise ValueError("`path` cannot be empty")
        current_node = self
        for path_component in path:
            current_node = current_node[path_component]
        return current_node

    def set_with_path(self, path: tuple, value: Any) -> None:
        """
        Set a value in the tree at the specified tuple path.
        Args:
            path (tuple): The path to traverse.
            value (Any): The value to set.
        Raises:
            ValueError: If the path is empty.
        """
        if not path:
            raise ValueError("`path` cannot be empty")
        current_node = self
        for path_component in path[:-1]:
            current_node = current_node[path_component]
        current_node[path[-1]] = value

    def del_at_path(self, path: tuple, strict: bool = True) -> None:
        """
        Delete a value in the tree at the specified tuple path.
        Args:
            path (tuple): The path to traverse.
            strict (bool): If True, raise an error if the path does not exist.
        Raises:
            ValueError: If the path is empty.
            LookupError: If the path does not exist and strict is True.
        """
        if not path:
            raise ValueError("`path` cannot be empty")
        try:
            current_node = self
            for path_component in path[:-1]:
                current_node = current_node[path_component]
            del current_node[path[-1]]
        except LookupError as err:
            if strict:
                raise err

    def get_longest_contained_prefix(self, path: tuple) -> tuple:
        """
        Find the longest prefix of the given path that exists in the tree.
        Args:
            path (tuple): The path to check.
        Returns:
            tuple: The longest contained prefix.
        """
        current_node = self
        prefix = ()
        for path_component in path:
            if path_component in current_node:
                current_node = current_node[path_component]
                prefix = (*prefix, path_component)
            else:
                break
        return prefix
