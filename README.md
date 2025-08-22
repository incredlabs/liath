# 🚀 Liath: Your AI-Powered Database System

> Liath is a next-generation database system that combines the power of key-value storage, vector search, and AI capabilities into one flexible platform. Built on RocksDB/LevelDB with Lua as its query language, it's designed for developers who want to build AI-powered applications quickly and efficiently.

[![PyPI version](https://badge.fury.io/py/liath.svg)](https://badge.fury.io/py/liath)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

Liath comes packed with powerful features to help you build AI-powered applications. Here's a quick overview:

- 🔌 **Pluggable Storage**: Choose between RocksDB and LevelDB
- 📝 **Lua Query Language**: Write powerful queries with familiar syntax
- 🧩 **Plugin Architecture**: Extend functionality with custom plugins
- 🔍 **Vector Search**: Built-in vector database capabilities
- 🤖 **AI Integration**: Direct access to language models
- 📊 **Embedding Generation**: Create and manage text embeddings
- 📁 **File Operations**: Built-in file storage and retrieval
- 🏷️ **Namespaces**: Isolate data and operations
- 💾 **Transaction Support**: ACID compliant (RocksDB)
- 🔐 **User Authentication**: Secure user management
- 🌐 **CLI & HTTP API**: Multiple ways to interact
- 💾 **Backup & Restore**: Keep your data safe
- ⚡ **Query Caching**: Optimize performance
- 📈 **Monitoring**: Track system performance
- 🔄 **Connection Pooling**: Handle high concurrency

> 📚 For detailed information about each feature, check out our [Features Documentation](FEATURES.md)

## 🛠️ Installation

### As a Library
```bash
pip install liath
```

### From Source
1. **Prerequisites**
   - Python 3.11 or higher
   - Poetry package manager

2. **Install Poetry**
   ```bash
   pip install poetry
   ```

3. **Clone & Setup**
   ```bash
   git clone https://github.com/nudgelang/liath.git
   cd liath
   poetry install
   ```

4. **Create Directory Structure**
   ```bash
   mkdir -p data/default/{files,luarocks} plugins
   ```

5. **Install Lua Dependencies**
   ```bash
   ./liath/setup_luarocks.sh
   ```

## 📦 Usage

### As a Library (Embedded Mode)
```python
from liath import EmbeddedLiath

# Create an embedded database instance
db = EmbeddedLiath(data_dir="./my_data", storage_type="auto")

# Basic operations
db.put("key", "value")
retrieved_value = db.get("key")
print(retrieved_value)  # Output: value

# Execute Lua queries
result = db.execute_lua('return db:get("key")')
print(result)  # Output: value

# Switch namespaces
db.set_namespace("my_namespace")
db.put("namespaced_key", "namespaced_value")

# Close the database when done
db.close()
```

### CLI Mode
```bash
liath-cli --storage auto
```

### Server Mode
```bash
liath-server --storage auto --host 0.0.0.0 --port 5000
```

### Basic Operations

```lua
-- Create user and login
create_user username password
login username password

-- Create and use namespace
create_namespace my_namespace
use my_namespace

-- Basic queries
query return db:put("key", "value")
query return db:get("key")
```

## 📦 Using LuaRocks Packages

Liath supports LuaRocks packages in your queries. Here's how:

1. **Install a Package**
   ```bash
   luarocks install --tree=./data/namespaces/your_namespace package_name
   ```

2. **Use in Queries**
   ```lua
   local json = db:require("cjson")
   return json.encode({key = "value"})
   ```

### Example: HTTP Requests with LuaSocket

```lua
local http = db:require("socket.http")
local body, code = http.request("http://example.com")
return {body = body, status_code = code}
```

## 🔄 Storage Options

Choose your storage backend based on your needs:

| Feature | RocksDB | LevelDB |
|---------|---------|---------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Transactions | ✅ | ❌ |
| Column Families | ✅ | ❌ |
| Complexity | Medium | Low |

## 🔧 API Reference

### EmbeddedLiath Class

The `EmbeddedLiath` class provides a Pythonic interface for interacting with the database.

#### Constructor
```python
db = EmbeddedLiath(data_dir="./data", storage_type="auto")
```

Parameters:
- `data_dir` (str): Directory to store database files
- `storage_type` (str): Storage backend ('auto', 'rocksdb', or 'leveldb')

#### Methods

##### `put(key, value)`
Store a key-value pair in the database.

##### `get(key)`
Retrieve a value from the database.

##### `delete(key)`
Delete a key-value pair from the database.

##### `execute_lua(query)`
Execute a Lua query.

##### `set_namespace(namespace)`
Switch to a different namespace.

##### `create_user(username, password)`
Create a new user.

##### `authenticate_user(username, password)`
Authenticate a user.

##### `list_namespaces()`
List all namespaces.

##### `close()`
Close the database connection.

### Direct Database Access

For more advanced usage, you can access the underlying `Database` class directly:

```python
from liath import Database

db = Database(data_dir="./data", storage_type="auto")
# ... use database methods directly
```

## 🧩 Extending Liath

Create custom plugins by:
1. Adding a new Python file in `plugins/`
2. Inheriting from `PluginBase`
3. Implementing required methods

### Example Plugin
```python
from liath.plugin_base import PluginBase

class MyPlugin(PluginBase):
    @property
    def name(self):
        return "myplugin"

    def initialize(self, context):
        self.namespace = context['namespace']

    def get_lua_interface(self):
        return {
            'my_function': self.lua_callable(self.my_function)
        }

    def my_function(self, arg1, arg2):
        # Your plugin logic here
        return f"Processed {arg1} and {arg2}"
```

## 📦 Using LuaRocks Packages

Liath supports LuaRocks packages in your queries. Here's how:

1. **Install a Package**
   ```bash
   luarocks install --tree=./data/namespaces/your_namespace package_name
   ```

2. **Use in Queries**
   ```lua
   local json = db:require("cjson")
   return json.encode({key = "value"})
   ```

### Example: HTTP Requests with LuaSocket

```lua
local http = db:require("socket.http")
local body, code = http.request("http://example.com")
return {body = body, status_code = code}
```

## 🤝 Contributing

We welcome contributions! Feel free to:
- Submit pull requests
- Report bugs
- Suggest features
- Improve documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.
