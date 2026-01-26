# Database Plugin (db)

The database plugin provides core CRUD operations. It's always available and accessed via `db` global (not `plugins.db`).

## Functions

### db:get(key)

Retrieve a value by key.

**Parameters:**

- `key` (string): The key to retrieve

**Returns:** string or nil

**Example:**
```lua
local value = db:get("user:1:name")
if value then
    return value
else
    return "Not found"
end
```

### db:put(key, value)

Store a value.

**Parameters:**

- `key` (string): The key to store
- `value` (string): The value to store

**Returns:** nil

**Example:**
```lua
db:put("user:1:name", "Alice")
db:put("user:1:email", "alice@example.com")
```

### db:delete(key)

Delete a key.

**Parameters:**

- `key` (string): The key to delete

**Returns:** nil

**Example:**
```lua
db:delete("user:1:temp")
```

### db:iterator()

Iterate over all keys and values.

**Returns:** table of {key: value} pairs

**Example:**
```lua
local items = db:iterator()
local count = 0
for _, item in ipairs(items) do
    for key, value in pairs(item) do
        count = count + 1
    end
end
return count
```

### db:write_batch(operations)

Perform multiple operations atomically.

**Parameters:**

- `operations` (table): Array of operation objects
  - `{type = "put", key = "...", value = "..."}`
  - `{type = "delete", key = "..."}`

**Returns:** nil

**Example:**
```lua
local ops = {
    {type = "put", key = "item:1", value = "Apple"},
    {type = "put", key = "item:2", value = "Banana"},
    {type = "delete", key = "item:old"}
}
db:write_batch(ops)
```

## Column Families (RocksDB only)

Column families provide logical partitioning within a namespace.

### db:create_column_family(name)

Create a column family.

```lua
db:create_column_family("users")
db:create_column_family("products")
```

### db:drop_column_family(name)

Drop a column family.

```lua
db:drop_column_family("old_data")
```

### db:list_column_families()

List all column families.

```lua
local families = db:list_column_families()
return families
```

### db:get_cf(cf_name, key)

Get from a column family.

```lua
local value = db:get_cf("users", "alice")
```

### db:put_cf(cf_name, key, value)

Put to a column family.

```lua
db:put_cf("users", "alice", '{"name": "Alice"}')
```

### db:delete_cf(cf_name, key)

Delete from a column family.

```lua
db:delete_cf("users", "old_user")
```

## Transactions (RocksDB only)

### db:begin_transaction()

Start a transaction.

```lua
db:begin_transaction()
db:put("key1", "value1")
db:put("key2", "value2")
db:commit_transaction()
```

### db:commit_transaction()

Commit the current transaction.

### db:rollback_transaction()

Rollback the current transaction.

```lua
db:begin_transaction()
db:put("key", "value")
-- Something went wrong
db:rollback_transaction()
```

## Maintenance (RocksDB only)

### db:compact_range(begin, end)

Compact a key range.

```lua
db:compact_range("a", "z")
```

### db:flush()

Flush memtables to disk.

```lua
db:flush()
```

## Usage Patterns

### Key Naming Convention

```lua
-- entity:id:attribute pattern
db:put("user:123:name", "Alice")
db:put("user:123:email", "alice@example.com")
db:put("product:456:title", "Widget")
```

### JSON Storage

```lua
local user = {name = "Alice", age = 30}
local json = require("cjson")
db:put("user:123", json.encode(user))

local data = json.decode(db:get("user:123"))
return data.name
```

### Counter Pattern

```lua
local current = tonumber(db:get("counter")) or 0
db:put("counter", tostring(current + 1))
return current + 1
```
