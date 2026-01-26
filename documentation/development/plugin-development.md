# Plugin Development Guide

Advanced guide for creating production-ready Liath plugins.

## Plugin Lifecycle

```
Database starts
    │
    ▼
load_plugins() discovers plugin classes
    │
    ▼
Plugin classes instantiated (no context yet)
    │
    ▼
Query execution begins
    │
    ▼
initialize(context) called with namespace info
    │
    ▼
get_lua_interface() called
    │
    ▼
Lua functions registered
    │
    ▼
Query executes, calling plugin functions
    │
    ▼
Database closes
    │
    ▼
Plugin cleanup (if implemented)
```

## Plugin Structure

### Minimal Plugin

```python
from liath.plugin_base import PluginBase
import json

class MinimalPlugin(PluginBase):
    def initialize(self, context):
        pass

    def get_lua_interface(self):
        return {
            'minimal_hello': self.lua_callable(self.hello)
        }

    @property
    def name(self):
        return "minimal"

    def hello(self):
        return json.dumps({"message": "Hello from minimal plugin"})
```

### Full-Featured Plugin

```python
from liath.plugin_base import PluginBase
import json
import threading
import logging

class AdvancedPlugin(PluginBase):
    """An advanced plugin with all features."""

    def __init__(self):
        """Called once when plugin is discovered."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._global_config = {}

    def initialize(self, context):
        """Called for each namespace before queries.

        Args:
            context: Dict with namespace, db, data_dir, packages
        """
        self.namespace = context.get('namespace')
        self.db = context.get('db')
        self.data_dir = context.get('data_dir')
        self.packages = context.get('packages')

        # Namespace-specific state
        self._cache = {}
        self._lock = threading.Lock()

        self.logger.info(f"Initialized for namespace: {self.namespace}")

    def get_lua_interface(self):
        """Return functions to expose to Lua."""
        return {
            'adv_get_data': self.lua_callable(self.get_data),
            'adv_set_data': self.lua_callable(self.set_data),
            'adv_process': self.lua_callable(self.process),
            'adv_batch': self.lua_callable(self.batch_operation),
        }

    @property
    def name(self):
        """Unique plugin identifier."""
        return "advanced"

    def get_data(self, key):
        """Retrieve data with caching."""
        with self._lock:
            if key in self._cache:
                return json.dumps({
                    "status": "success",
                    "value": self._cache[key],
                    "cached": True
                })

        value = self.db.get(f"adv:{key}")
        if value:
            with self._lock:
                self._cache[key] = value
            return json.dumps({
                "status": "success",
                "value": value,
                "cached": False
            })

        return json.dumps({
            "status": "error",
            "message": "Key not found"
        })

    def set_data(self, key, value):
        """Store data and invalidate cache."""
        try:
            self.db.put(f"adv:{key}", value)
            with self._lock:
                self._cache[key] = value
            return json.dumps({"status": "success"})
        except Exception as e:
            self.logger.error(f"Failed to set data: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    def process(self, data):
        """Process data with validation."""
        try:
            parsed = json.loads(data)
            # Validate
            if 'input' not in parsed:
                return json.dumps({
                    "status": "error",
                    "message": "Missing 'input' field"
                })

            # Process
            result = self._do_processing(parsed['input'])

            return json.dumps({
                "status": "success",
                "result": result
            })
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "message": "Invalid JSON"
            })
        except Exception as e:
            self.logger.exception("Processing failed")
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

    def batch_operation(self, items_json):
        """Process multiple items."""
        try:
            items = json.loads(items_json)
            results = []

            for item in items:
                result = self._process_single(item)
                results.append(result)

            return json.dumps({
                "status": "success",
                "results": results,
                "count": len(results)
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

    def _do_processing(self, input_data):
        """Internal processing logic."""
        return input_data.upper()

    def _process_single(self, item):
        """Process a single item."""
        return {"processed": True, "item": item}

    def shutdown(self):
        """Optional cleanup method."""
        self.logger.info("Shutting down advanced plugin")
        self._cache.clear()
```

## Best Practices

### Error Handling

Always catch exceptions and return JSON errors:

```python
def risky_operation(self, param):
    try:
        result = self._do_risky_thing(param)
        return json.dumps({"status": "success", "result": result})
    except ValueError as e:
        return json.dumps({"status": "error", "type": "validation", "message": str(e)})
    except IOError as e:
        return json.dumps({"status": "error", "type": "io", "message": str(e)})
    except Exception as e:
        self.logger.exception("Unexpected error")
        return json.dumps({"status": "error", "type": "internal", "message": "Internal error"})
```

### Thread Safety

Use locks for shared state:

```python
def __init__(self):
    self._lock = threading.Lock()
    self._shared_state = {}

def thread_safe_update(self, key, value):
    with self._lock:
        self._shared_state[key] = value
    return json.dumps({"status": "success"})
```

### Resource Management

Clean up resources properly:

```python
def initialize(self, context):
    self._connection = self._create_connection()

def shutdown(self):
    if hasattr(self, '_connection'):
        self._connection.close()
```

### Configuration

Support plugin configuration:

```python
def initialize(self, context):
    self.db = context.get('db')

    # Load plugin config from database
    config_json = self.db.get("__plugin_config:myplugin")
    if config_json:
        self.config = json.loads(config_json)
    else:
        self.config = self._default_config()

def _default_config(self):
    return {
        "cache_ttl": 300,
        "max_batch_size": 100
    }
```

### Logging

Use Python logging:

```python
import logging

class MyPlugin(PluginBase):
    def __init__(self):
        self.logger = logging.getLogger("liath.plugins.myplugin")

    def some_operation(self):
        self.logger.debug("Starting operation")
        self.logger.info("Operation completed")
        self.logger.warning("Deprecated method used")
        self.logger.error("Operation failed")
```

## Testing Plugins

### Unit Testing

```python
import pytest
import json
from my_plugin import MyPlugin

class MockDB:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value

@pytest.fixture
def plugin():
    p = MyPlugin()
    p.initialize({
        'namespace': 'test',
        'db': MockDB(),
        'data_dir': '/tmp/test',
        'packages': ''
    })
    return p

def test_hello(plugin):
    result = plugin.hello("World")
    data = json.loads(result)
    assert data['status'] == 'success'
    assert 'World' in data['message']

def test_error_handling(plugin):
    result = plugin.risky_operation(None)
    data = json.loads(result)
    assert data['status'] == 'error'
```

### Integration Testing

```python
import pytest
from liath import Database, EmbeddedLiath

def test_plugin_integration():
    db = EmbeddedLiath(data_dir="/tmp/test_data")

    result = db.execute_lua('''
        return plugins.myplugin.myplugin_hello("World")
    ''')

    data = json.loads(result)
    assert data['status'] == 'success'

    db.close()
```

## Packaging Plugins

### Directory Structure

```
my_liath_plugins/
├── __init__.py
├── my_plugin.py
├── another_plugin.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### Loading Custom Plugins

```python
from liath import Database

db = Database(
    data_dir="./data",
    plugins_dir="./my_liath_plugins"
)
```

### Publishing as Package

Create a Python package:

```
my-liath-plugin/
├── pyproject.toml
├── README.md
├── liath_myplugin/
│   ├── __init__.py
│   └── plugin.py
└── tests/
    └── test_plugin.py
```

pyproject.toml:
```toml
[tool.poetry]
name = "liath-myplugin"
version = "0.1.0"
description = "My custom Liath plugin"

[tool.poetry.dependencies]
python = ">=3.11"
liath = ">=0.1.0"

[tool.poetry.plugins."liath.plugins"]
myplugin = "liath_myplugin.plugin:MyPlugin"
```
