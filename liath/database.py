"""
Core database module for Liath.

This module provides the main Database class that orchestrates storage,
plugins, namespaces, and Lua query execution.
"""

from lupa import LuaRuntime, lua_type
import json
import yaml
import os
import threading
import importlib.util
import inspect
import tempfile
import shutil
import subprocess
import hashlib
import binascii

from liath.plugin_base import PluginBase
from liath.storage.leveldb_storage import LevelDBStorage

# Lazy import for RocksDB to avoid import error when not installed
RocksDBStorage = None
try:
    from liath.storage.rocksdb_storage import RocksDBStorage
except ImportError:
    pass  # RocksDB not available


class Database:
    """Main database class for managing namespaces, plugins, and query execution.

    The Database class is the central orchestrator for Liath. It manages:
    - Multiple isolated namespaces, each with its own storage and Lua context
    - Plugin loading and initialization
    - Lua query execution with access to storage and plugins
    - User authentication with secure password hashing

    Args:
        data_dir: Directory for storing database files. Defaults to './data'.
        plugins_dir: Optional directory for additional custom plugins.
        storage_type: Storage backend to use. Options:
            - 'auto': Try RocksDB first, fall back to LevelDB
            - 'rocksdb': Use RocksDB (requires rocksdb package)
            - 'leveldb': Use LevelDB

    Attributes:
        data_dir: Path to the data directory.
        plugins_dir: Path to custom plugins directory (if provided).
        namespaces: Dict mapping namespace names to their storage and metadata.
        plugins: Dict mapping plugin names to plugin instances.

    Example:
        >>> db = Database(data_dir='./my_data', storage_type='auto')
        >>> db.create_namespace('users')
        >>> result = db.execute_query('users', 'return db:get("key")')
        >>> db.close()
    """

    def __init__(self, data_dir='./data', plugins_dir=None, storage_type='auto'):
        self.data_dir = data_dir
        # User-provided plugins directory (optional)
        self.plugins_dir = plugins_dir
        self.namespaces = {}
        self.metadata_file = os.path.join(data_dir, 'metadata.json')
        
        if storage_type == 'auto':
            if RocksDBStorage is not None:
                self.StorageClass = RocksDBStorage
            else:
                self.StorageClass = LevelDBStorage
        elif storage_type == 'rocksdb':
            if RocksDBStorage is None:
                raise ImportError(
                    "RocksDB backend requires the 'python-rocksdb' package. "
                    "Install with: pip install liath[rocksdb]"
                )
            self.StorageClass = RocksDBStorage
        elif storage_type == 'leveldb':
            self.StorageClass = LevelDBStorage
        else:
            raise ValueError("Invalid storage_type. Choose 'auto', 'rocksdb', or 'leveldb'")

        self.auth_db = self.StorageClass(os.path.join(data_dir, "auth.db"))
        # Load plugins from packaged location and optional user directory
        self.plugins = self.load_plugins()
        self.load_metadata()

    def _configure_lua_paths(self, lua: LuaRuntime, namespace: str):
        """Configure Lua package paths for module loading.

        Sets up Lua's package.path and package.cpath to include:
        - User-level LuaRocks modules (~/.luarocks/)
        - Namespace-specific LuaRocks modules

        Args:
            lua: The Lua runtime instance to configure.
            namespace: The namespace name for namespace-specific paths.
        """
        # Configure Lua package paths to include user-level luarocks and namespace-specific tree
        setup_script = f"""
            local home = os.getenv("HOME")
            local lua_version = _VERSION:match("%d+%.%d+")
            package.path = package.path .. ";" .. home .. "/.luarocks/share/lua/" .. lua_version .. "/?.lua"
            package.path = package.path .. ";" .. home .. "/.luarocks/share/lua/" .. lua_version .. "/?/init.lua"
            package.cpath = package.cpath .. ";" .. home .. "/.luarocks/lib/lua/" .. lua_version .. "/?.so"

            local ns_path = "{os.path.join(self.data_dir, 'namespaces', namespace)}"
            package.path = package.path .. ";" .. ns_path .. "/share/lua/" .. lua_version .. "/?.lua"
            package.path = package.path .. ";" .. ns_path .. "/share/lua/" .. lua_version .. "/?/init.lua"
            package.cpath = package.cpath .. ";" .. ns_path .. "/lib/lua/" .. lua_version .. "/?.so"
        """
        lua.execute(setup_script)

    def load_plugins(self):
        """Discover and load plugins from plugin directories.

        Scans the packaged plugins directory and optional user-provided
        directory for Python modules containing PluginBase subclasses.

        Returns:
            Dict mapping plugin names to plugin instances.

        Note:
            Faulty plugins are silently skipped to prevent breaking core
            functionality.
        """
        plugins = {}
        candidate_dirs = []
        # Packaged plugins directory
        packaged_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if os.path.isdir(packaged_dir):
            candidate_dirs.append(packaged_dir)
        # Optional user-provided directory
        if self.plugins_dir and os.path.isdir(self.plugins_dir):
            candidate_dirs.append(self.plugins_dir)

        for d in candidate_dirs:
            for filename in os.listdir(d):
                if not filename.endswith('.py'):
                    continue
                module_name = f"liath_user_plugin_{filename[:-3]}_{abs(hash(d))}"
                module_path = os.path.join(d, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)  # type: ignore
                except Exception:
                    # Skip faulty plugins silently to avoid breaking core
                    continue

                for _, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        try:
                            plugin = obj()
                            plugins[plugin.name] = plugin
                        except Exception:
                            continue
        return plugins

    def load_metadata(self):
        """Load namespace metadata from the metadata file.

        Reads metadata.json and creates namespaces with their stored
        configurations. If no metadata file exists, creates the default
        namespace.
        """
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                for name, info in metadata.items():
                    self.create_namespace(name, info.get('packages'))
        else:
            self.create_namespace('default')

    def save_metadata(self):
        """Persist namespace metadata to the metadata file.

        Writes the current namespace configurations (including installed
        packages) to metadata.json for persistence across restarts.
        """
        metadata = {name: {'packages': list(info['packages'])} for name, info in self.namespaces.items()}
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f)

    def create_namespace(self, name, packages=None):
        """Create a new isolated namespace.

        Creates a namespace with its own storage database, thread lock,
        and LuaRocks module tree. Namespaces provide complete data
        isolation.

        Args:
            name: Unique name for the namespace.
            packages: Optional set of pre-installed LuaRocks packages.

        Note:
            If the namespace already exists, this is a no-op.
        """
        if name not in self.namespaces:
            db_path = os.path.join(self.data_dir, f"{name}.db")
            self.namespaces[name] = {
                'db': self.StorageClass(db_path),
                'lock': threading.Lock(),
                'packages': set(packages or []),
            }
            self.save_metadata()
            # Ensure namespace LuaRocks tree exists
            ns_root = os.path.join(self.data_dir, 'namespaces', name)
            for p in [
                os.path.join(ns_root, 'share', 'lua'),
                os.path.join(ns_root, 'lib', 'lua'),
            ]:
                os.makedirs(p, exist_ok=True)
       
    def execute_query(self, namespace, query, return_format='dict'):
        """Execute a Lua query in a namespace context.

        Creates a Lua runtime, initializes plugins, and executes the
        provided Lua code with access to the database and plugins.

        Args:
            namespace: The namespace to execute the query in.
            query: Lua code to execute. Should typically include a return
                statement for results.
            return_format: Output format. Options:
                - 'dict': Python dictionary (default)
                - 'json': JSON string
                - 'yaml': YAML string
                - 'markdown': Markdown formatted string

        Returns:
            Query result in the specified format.

        Raises:
            ValueError: If the namespace doesn't exist or format is invalid.

        Example:
            >>> result = db.execute_query('default', 'return db:get("key")')
            >>> result = db.execute_query('default', '''
            ...     db:put("key", "value")
            ...     return db:get("key")
            ... ''', return_format='json')
        """
        if namespace not in self.namespaces:
            raise ValueError(f"Namespace '{namespace}' does not exist")

        with self.namespaces[namespace]['lock']:
            context = {
                'namespace': namespace,
                'db': self.namespaces[namespace]['db'],
                'packages': self.namespaces[namespace]['packages'],
                'data_dir': self.data_dir
            }

            # Initialize plugins and build plugins table for Lua
            plugins_table = {}
            for plugin in self.plugins.values():
                plugin.initialize(context)
                plugins_table[plugin.name] = plugin.get_lua_interface()

            # Create Lua runtime and configure paths
            lua = LuaRuntime(unpack_returned_tuples=True)
            self._configure_lua_paths(lua, namespace)

            # Expose database and plugins as Lua globals
            lua.globals()['db'] = self.namespaces[namespace]['db']
            lua.globals()['plugins'] = plugins_table

            # Execute the Lua query
            # Wrap the query in a function and return its result
            wrapped_query = f"""
            function execute_query()
                {query}
            end
            return execute_query()
            """

            # Execute the Lua query
            result = lua.execute(wrapped_query)

            return self._format_result(result, return_format)

    def _format_result(self, result, format):
        """Format a Lua query result for output.

        Args:
            result: Raw result from Lua execution.
            format: Target format ('dict', 'json', 'yaml', 'markdown').

        Returns:
            Formatted result in the specified format.

        Raises:
            ValueError: If format is not supported.
        """
        if format == 'dict':
            return self._lua_to_python(result)
        elif format == 'json':
            return json.dumps(self._lua_to_python(result))
        elif format == 'yaml':
            return yaml.dump(self._lua_to_python(result))
        elif format == 'markdown':
            return self._dict_to_markdown(self._lua_to_python(result))
        else:
            raise ValueError(f"Unsupported return format: {format}")

    def _lua_to_python(self, obj):
        """Recursively convert Lua objects to Python equivalents.

        Handles conversion of Lua tables to Python lists/dicts,
        and Lua primitives to Python types.

        Args:
            obj: Lua object to convert.

        Returns:
            Python equivalent of the Lua object.
        """
        lua_type_name = lua_type(obj)
        if lua_type_name == 'table':
            if len(obj) > 0:
                return [self._lua_to_python(item) for item in obj.values()]
            else:
                return {str(k): self._lua_to_python(v) for k, v in obj.items()}
        elif lua_type_name == 'unicode':
            return str(obj)
        elif lua_type_name in ['int', 'long', 'float']:
            return obj
        elif lua_type_name == 'NoneType':
            return None
        else:
            return str(obj)

    def _dict_to_markdown(self, d, level=0):
        """Convert a dictionary to markdown formatted string.

        Args:
            d: Dictionary to convert.
            level: Indentation level for nested structures.

        Returns:
            Markdown formatted string representation.
        """
        markdown = ""
        for key, value in d.items():
            markdown += "  " * level + f"- **{key}**: "
            if isinstance(value, dict):
                markdown += "\n" + self._dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                markdown += "\n" + "  " * (level + 1) + "- " + "\n  ".join(str(item) for item in value)
            else:
                markdown += str(value) + "\n"
        return markdown

    def authenticate_user(self, username, password):
        """Authenticate a user with username and password.

        Verifies the password against the stored hash using PBKDF2-HMAC-SHA256.
        Supports legacy plaintext passwords for backwards compatibility.

        Args:
            username: The username to authenticate.
            password: The password to verify.

        Returns:
            True if authentication succeeds, False otherwise.
        """
        stored = self.auth_db.get(username)
        if stored is None:
            return False
        # Support legacy plaintext entries
        if not isinstance(stored, str):
            try:
                stored = stored.decode('utf-8')
            except Exception:
                pass
        if stored and not stored.startswith('v1$'):
            return stored == password
        try:
            _, salt_hex, hash_hex = stored.split('$', 2)
            salt = binascii.unhexlify(salt_hex)
            expected = binascii.unhexlify(hash_hex)
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
            return dk == expected
        except Exception:
            return False

    def create_user(self, username, password):
        """Create a new user with secure password hashing.

        Stores the password using PBKDF2-HMAC-SHA256 with a random salt
        and 200,000 iterations.

        Args:
            username: Unique username for the new user.
            password: Password to hash and store.

        Raises:
            ValueError: If a user with the username already exists.
        """
        if self.auth_db.get(username) is not None:
            raise ValueError("User already exists")
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
        value = 'v1$' + binascii.hexlify(salt).decode('ascii') + '$' + binascii.hexlify(dk).decode('ascii')
        self.auth_db.put(username, value)

    def list_namespaces(self):
        """Get a list of all namespace names.

        Returns:
            List of namespace name strings.
        """
        return list(self.namespaces.keys())

    def install_package(self, namespace, package):
        """Install a LuaRocks package for a specific namespace.

        Downloads and installs the package into the namespace's LuaRocks
        tree, making it available for Lua queries in that namespace.

        Args:
            namespace: The namespace to install the package for.
            package: The LuaRocks package name to install.

        Returns:
            True if installation succeeds, False otherwise.

        Raises:
            ValueError: If the namespace doesn't exist.

        Note:
            Requires 'luarocks' to be installed and available in PATH.
        """
        if namespace not in self.namespaces:
            raise ValueError(f"Namespace '{namespace}' does not exist")
        ns_root = os.path.join(self.data_dir, 'namespaces', namespace)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                subprocess.run(['luarocks', 'install', package, f'--tree={temp_dir}'], check=True)
                # Copy only lib/ and share/ trees
                for sub in ('lib', 'share'):
                    s = os.path.join(temp_dir, sub)
                    if os.path.isdir(s):
                        d = os.path.join(ns_root, sub)
                        os.makedirs(d, exist_ok=True)
                        shutil.copytree(s, d, dirs_exist_ok=True)
                self.namespaces[namespace]['packages'].add(package)
                self.save_metadata()
                return True
            except subprocess.CalledProcessError:
                return False
            
    def close(self):
        """Close all database connections and release resources.

        Closes all namespace storage backends and the authentication
        database. Should be called when the database is no longer needed.
        """
        for namespace in self.namespaces.values():
            namespace['db'].close()
        self.auth_db.close()

if __name__ == "__main__":
    db = Database()
    print("Database initialized with namespaces:", db.list_namespaces())
    print("Loaded plugins:", list(db.plugins.keys()))
