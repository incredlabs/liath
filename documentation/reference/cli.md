# CLI Reference

The Liath CLI provides an interactive interface for database operations.

## Starting the CLI

```bash
liath-cli [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--storage` | `auto` | Storage backend: `auto`, `rocksdb`, `leveldb` |
| `--data-dir` | `./data` | Data directory path |
| `--plugins-dir` | None | Additional plugins directory |
| `--help` | - | Show help message |

### Examples

```bash
# Default configuration
liath-cli

# Specify storage backend
liath-cli --storage rocksdb

# Custom data directory
liath-cli --data-dir /var/lib/liath/data

# With custom plugins
liath-cli --plugins-dir ./my_plugins
```

## Commands

### login

Authenticate with username and password.

```
login <username> <password>
```

**Example:**
```
> login admin admin123
Logged in as admin
```

### use

Switch to a namespace.

```
use <namespace>
```

**Example:**
```
> use production
Switched to namespace: production
```

### create_namespace

Create a new namespace.

```
create_namespace <name>
```

**Example:**
```
> create_namespace users
Namespace 'users' created
```

### list_namespaces

List all available namespaces.

```
list_namespaces
```

**Example:**
```
> list_namespaces
Available namespaces:
  - default
  - users
  - products
```

### query

Execute a Lua query.

```
query <lua_code>
```

For multi-line queries, end with `;;`:

```
query
... local value = db:get("key")
... return value
... ;;
```

**Examples:**
```
> query return db:get("name")
Alice

> query
... local items = {}
... for i = 1, 5 do
...     items[i] = "Item " .. i
... end
... return items
... ;;
["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
```

### set_format

Set the output format for query results.

```
set_format <format>
```

Available formats:

| Format | Description |
|--------|-------------|
| `dict` | Python dictionary (default) |
| `json` | JSON string |
| `yaml` | YAML string |
| `lua` | Lua table notation |

**Example:**
```
> set_format json
Output format set to: json

> query return {name = "Alice", age = 30}
{"name": "Alice", "age": 30}
```

### exit / quit

Exit the CLI.

```
exit
```

or

```
quit
```

## Interactive Session Example

```
$ liath-cli --data-dir ./my_data

Liath Database CLI
Type 'help' for available commands.

> login admin admin123
Logged in as admin

> use default
Switched to namespace: default

> query db:put("greeting", "Hello, World!")
nil

> query return db:get("greeting")
Hello, World!

> create_namespace users
Namespace 'users' created

> use users
Switched to namespace: users

> query db:put("alice", '{"name": "Alice", "role": "admin"}')
nil

> set_format json
Output format set to: json

> query return db:get("alice")
{"name": "Alice", "role": "admin"}

> list_namespaces
Available namespaces:
  - default
  - users

> exit
Goodbye!
```

## Multi-line Queries

For complex queries spanning multiple lines:

1. Type `query` and press Enter
2. Enter your Lua code line by line
3. End with `;;` on its own line

```
> query
... local function fibonacci(n)
...     if n <= 1 then return n end
...     return fibonacci(n-1) + fibonacci(n-2)
... end
...
... local results = {}
... for i = 0, 10 do
...     results[i+1] = fibonacci(i)
... end
... return results
... ;;
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

## Error Handling

The CLI displays errors from queries:

```
> query return db:get()
Error: bad argument #1 to 'get' (string expected, got nil)

> query return nonexistent_function()
Error: attempt to call global 'nonexistent_function' (a nil value)
```

## Tips

1. **Tab completion**: Some terminals support tab completion for commands
2. **Command history**: Use up/down arrows to navigate command history
3. **Escape quotes**: In queries, escape quotes: `db:put("key", "value with \"quotes\"")`
4. **JSON in queries**: For JSON values, use single quotes outside: `db:put('key', '{"a": 1}')`
