"""
Plugin base class for Liath plugins.

This module provides the abstract base class that all Liath plugins
must inherit from.
"""

from abc import ABC, abstractmethod
from lupa import unpacks_lua_table


class PluginBase(ABC):
    """Abstract base class for Liath plugins.

    All plugins must inherit from this class and implement the required
    abstract methods. Plugins expose functionality to Lua queries through
    the `get_lua_interface` method.

    Example:
        >>> class MyPlugin(PluginBase):
        ...     def initialize(self, context):
        ...         self.db = context.get('db')
        ...
        ...     def get_lua_interface(self):
        ...         return {
        ...             'my_function': self.lua_callable(self.my_function)
        ...         }
        ...
        ...     @property
        ...     def name(self):
        ...         return "myplugin"
        ...
        ...     def my_function(self, arg):
        ...         return json.dumps({"result": arg})
    """

    @abstractmethod
    def initialize(self, context):
        """Initialize the plugin with namespace context.

        Called before each query execution to set up the plugin for
        the current namespace.

        Args:
            context: Dict containing:
                - 'namespace': The namespace name (str)
                - 'db': The storage backend instance (StorageBase)
                - 'data_dir': Path to the data directory (str)
                - 'packages': Set of installed LuaRocks packages
        """
        pass

    @abstractmethod
    def get_lua_interface(self):
        """Return functions to expose to Lua.

        Returns:
            Dict mapping Lua function names to Python callables.
            Use `lua_callable` decorator on methods to ensure proper
            type conversion.

        Example:
            >>> def get_lua_interface(self):
            ...     return {
            ...         'plugin_greet': self.lua_callable(self.greet),
            ...         'plugin_compute': self.lua_callable(self.compute),
            ...     }
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """Unique identifier for the plugin.

        This name is used as the key in `plugins.{name}` when accessed
        from Lua.

        Returns:
            str: Unique plugin name (e.g., 'db', 'embed', 'vdb').
        """
        pass

    @staticmethod
    def lua_callable(func):
        """Decorator to make a method callable from Lua.

        Wraps the function to properly unpack Lua tables passed as
        arguments, enabling seamless Python-Lua interop.

        Args:
            func: The function to wrap.

        Returns:
            Wrapped function that handles Lua table unpacking.

        Example:
            >>> def get_lua_interface(self):
            ...     return {
            ...         'my_func': self.lua_callable(self.my_func)
            ...     }
        """
        @unpacks_lua_table
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper