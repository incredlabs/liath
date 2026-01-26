# Building Plugins

Learn how to extend Liath with custom plugins.

## Plugin Architecture

Liath plugins:

- Inherit from `PluginBase`
- Define functions exposed to Lua
- Are initialized per-namespace
- Can access database and other plugins

## Basic Plugin Structure

```python
# my_plugin.py
from liath.plugin_base import PluginBase
import json

class MyPlugin(PluginBase):
    """A custom plugin example."""

    def initialize(self, context):
        """Called when the plugin is initialized for a namespace.

        Args:
            context: Dict with 'namespace', 'db', 'data_dir', 'packages'
        """
        self.namespace = context.get('namespace')
        self.db = context.get('db')
        self.data_dir = context.get('data_dir')

    def get_lua_interface(self):
        """Return functions to expose to Lua.

        Returns:
            Dict mapping Lua function names to Python callables
        """
        return {
            'my_hello': self.lua_callable(self.hello),
            'my_add': self.lua_callable(self.add_numbers),
        }

    @property
    def name(self):
        """Unique plugin identifier."""
        return "my"

    def hello(self, name):
        """Say hello to someone."""
        return json.dumps({
            "status": "success",
            "message": f"Hello, {name}!"
        })

    def add_numbers(self, a, b):
        """Add two numbers."""
        result = float(a) + float(b)
        return json.dumps({
            "status": "success",
            "result": result
        })
```

## Plugin Methods

### initialize(context)

Called when a namespace is initialized. Use this to set up resources.

```python
def initialize(self, context):
    self.namespace = context.get('namespace')
    self.db = context.get('db')  # Storage instance
    self.data_dir = context.get('data_dir')
    self.packages = context.get('packages')  # LuaRocks path

    # Initialize plugin-specific resources
    self.cache = {}
```

### get_lua_interface()

Return a dict of functions accessible from Lua:

```python
def get_lua_interface(self):
    return {
        'prefix_function_name': self.lua_callable(self.python_method),
    }
```

The dict keys become Lua function names: `plugins.prefix.function_name()`

### name property

Return a unique identifier for the plugin:

```python
@property
def name(self):
    return "myplugin"
```

This determines the `plugins.{name}` prefix in Lua.

## The lua_callable Decorator

Wrap methods to make them Lua-compatible:

```python
def get_lua_interface(self):
    return {
        'my_func': self.lua_callable(self.my_func),
    }
```

This handles:

- Type conversion between Lua and Python
- Error handling
- Return value serialization

## Returning Data

Return JSON strings for complex data:

```python
import json

def get_user(self, user_id):
    user = self.db.get(f"user:{user_id}")
    if user:
        return json.dumps({"status": "success", "user": json.loads(user)})
    else:
        return json.dumps({"status": "error", "message": "User not found"})
```

## Accessing the Database

Use the `db` object from context:

```python
def initialize(self, context):
    self.db = context.get('db')

def store_data(self, key, value):
    self.db.put(key, value)
    return json.dumps({"status": "success"})

def get_data(self, key):
    value = self.db.get(key)
    return json.dumps({"status": "success", "value": value})
```

## Error Handling

Handle errors gracefully:

```python
def risky_operation(self, param):
    try:
        result = self._do_something(param)
        return json.dumps({"status": "success", "result": result})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Unexpected error: {e}"})
```

## Loading Custom Plugins

### Directory-Based Loading

Place plugins in a directory:

```
my_plugins/
├── my_plugin.py
├── another_plugin.py
└── utils/
    └── helpers.py
```

Load them:

```python
from liath import Database

db = Database(
    data_dir="./data",
    plugins_dir="./my_plugins"
)
```

### Using Custom Plugins

```python
result = db.execute_query("default", '''
    local result = plugins.my.my_hello("World")
    return result
''')
print(result)  # {"status": "success", "message": "Hello, World!"}
```

## Complete Example: Counter Plugin

```python
# counter_plugin.py
from liath.plugin_base import PluginBase
import json
import threading

class CounterPlugin(PluginBase):
    """A thread-safe counter plugin."""

    def initialize(self, context):
        self.db = context.get('db')
        self.namespace = context.get('namespace')
        self.lock = threading.Lock()

    def get_lua_interface(self):
        return {
            'counter_get': self.lua_callable(self.get_counter),
            'counter_increment': self.lua_callable(self.increment),
            'counter_decrement': self.lua_callable(self.decrement),
            'counter_reset': self.lua_callable(self.reset),
        }

    @property
    def name(self):
        return "counter"

    def _get_key(self, counter_name):
        return f"__counter:{counter_name}"

    def get_counter(self, counter_name):
        key = self._get_key(counter_name)
        value = self.db.get(key)
        count = int(value) if value else 0
        return json.dumps({"status": "success", "value": count})

    def increment(self, counter_name, amount="1"):
        with self.lock:
            key = self._get_key(counter_name)
            current = int(self.db.get(key) or "0")
            new_value = current + int(amount)
            self.db.put(key, str(new_value))
            return json.dumps({"status": "success", "value": new_value})

    def decrement(self, counter_name, amount="1"):
        return self.increment(counter_name, str(-int(amount)))

    def reset(self, counter_name):
        key = self._get_key(counter_name)
        self.db.put(key, "0")
        return json.dumps({"status": "success", "value": 0})
```

Usage:

```python
result = db.execute_lua('''
    plugins.counter.counter_increment("visits")
    plugins.counter.counter_increment("visits")
    return plugins.counter.counter_get("visits")
''')
# {"status": "success", "value": 2}
```

## Testing Plugins

Test your plugins:

```python
import pytest
from my_plugin import MyPlugin

def test_my_plugin():
    plugin = MyPlugin()

    # Mock context
    context = {
        'namespace': 'test',
        'db': MockDB(),
        'data_dir': '/tmp/test',
        'packages': ''
    }

    plugin.initialize(context)

    # Test functions
    result = plugin.hello("Test")
    assert '"status": "success"' in result
    assert "Test" in result

class MockDB:
    def __init__(self):
        self.data = {}
    def get(self, key):
        return self.data.get(key)
    def put(self, key, value):
        self.data[key] = value
```

## Best Practices

1. **Use JSON for returns**: Always return JSON strings for complex data
2. **Handle errors**: Never let exceptions propagate to Lua
3. **Thread safety**: Use locks for shared state
4. **Prefix functions**: Use descriptive prefixes (`counter_`, `cache_`, etc.)
5. **Document functions**: Add docstrings for generated API docs
6. **Test thoroughly**: Unit test before integrating

## Next Steps

- [Plugin Development Guide](../development/plugin-development.md) - Advanced patterns
- [Built-in Plugins](../plugins/overview.md) - See existing implementations
