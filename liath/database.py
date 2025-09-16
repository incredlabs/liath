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
from liath.storage.rocksdb_storage import RocksDBStorage
from liath.storage.leveldb_storage import LevelDBStorage

class Database:
    def __init__(self, data_dir='./data', plugins_dir=None, storage_type='auto'):
        self.data_dir = data_dir
        # User-provided plugins directory (optional)
        self.plugins_dir = plugins_dir
        self.namespaces = {}
        self.metadata_file = os.path.join(data_dir, 'metadata.json')
        
        if storage_type == 'auto':
            try:
                import rocksdb
                self.StorageClass = RocksDBStorage
            except ImportError:
                self.StorageClass = LevelDBStorage
        elif storage_type == 'rocksdb':
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
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                for name, info in metadata.items():
                    self.create_namespace(name, info.get('packages'))
        else:
            self.create_namespace('default')

    def save_metadata(self):
        metadata = {name: {'packages': list(info['packages'])} for name, info in self.namespaces.items()}
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f)

    def create_namespace(self, name, packages=None):
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
        if self.auth_db.get(username) is not None:
            raise ValueError("User already exists")
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
        value = 'v1$' + binascii.hexlify(salt).decode('ascii') + '$' + binascii.hexlify(dk).decode('ascii')
        self.auth_db.put(username, value)

    def list_namespaces(self):
        return list(self.namespaces.keys())

    def install_package(self, namespace, package):
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
        for namespace in self.namespaces.values():
            namespace['db'].close()
        self.auth_db.close()

if __name__ == "__main__":
    db = Database()
    print("Database initialized with namespaces:", db.list_namespaces())
    print("Loaded plugins:", list(db.plugins.keys()))
