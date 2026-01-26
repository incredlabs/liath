# Basic Operations

This tutorial covers fundamental CRUD (Create, Read, Update, Delete) operations in Liath.

## Setting Up

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./tutorial_data")
```

## Create (Put)

Store values with the `put` method:

```python
# Simple string values
db.put("name", "Alice")
db.put("age", "30")

# JSON-like structured data (stored as string)
import json
user_data = json.dumps({
    "name": "Bob",
    "email": "bob@example.com",
    "roles": ["admin", "user"]
})
db.put("user:bob", user_data)
```

### Using Lua

```python
db.execute_lua('db:put("config:version", "1.0.0")')

# Store multiple values
db.execute_lua('''
    db:put("item:1", "Apple")
    db:put("item:2", "Banana")
    db:put("item:3", "Cherry")
    return "Items stored"
''')
```

## Read (Get)

Retrieve values with the `get` method:

```python
# Get a single value
name = db.get("name")
print(name)  # Output: Alice

# Handle missing keys
missing = db.get("nonexistent")
print(missing)  # Output: None
```

### Using Lua

```python
# Simple get
result = db.execute_lua('return db:get("name")')

# Get with fallback
result = db.execute_lua('''
    local value = db:get("missing_key")
    if value then
        return value
    else
        return "default_value"
    end
''')
```

## Update

Update is the same as put - it overwrites the existing value:

```python
# Original value
db.put("counter", "0")

# Update
db.put("counter", "1")
print(db.get("counter"))  # Output: 1
```

### Conditional Update in Lua

```python
# Read-modify-write pattern
result = db.execute_lua('''
    local current = db:get("counter") or "0"
    local new_value = tostring(tonumber(current) + 1)
    db:put("counter", new_value)
    return new_value
''')
print(result)  # Output: 2
```

## Delete

Remove values with the `delete` method:

```python
# Delete a key
db.delete("name")
print(db.get("name"))  # Output: None
```

### Using Lua

```python
db.execute_lua('db:delete("config:version")')

# Delete multiple keys
db.execute_lua('''
    db:delete("item:1")
    db:delete("item:2")
    db:delete("item:3")
    return "Items deleted"
''')
```

## Iteration

Iterate over all keys using Lua:

```python
# Store some data
db.put("user:1", "Alice")
db.put("user:2", "Bob")
db.put("user:3", "Charlie")

# Iterate all keys
result = db.execute_lua('''
    local items = db:iterator()
    local users = {}
    for _, item in ipairs(items) do
        for key, value in pairs(item) do
            if key:match("^user:") then
                table.insert(users, value)
            end
        end
    end
    return users
''')
print(result)  # Output: ['Alice', 'Bob', 'Charlie']
```

## Batch Operations

Perform multiple operations atomically:

```python
result = db.execute_lua('''
    local ops = {
        {type = "put", key = "batch:1", value = "Value 1"},
        {type = "put", key = "batch:2", value = "Value 2"},
        {type = "delete", key = "old_key"}
    }
    return db:write_batch(ops)
''')
```

## Error Handling

Handle errors gracefully:

```python
try:
    value = db.get("some_key")
    if value is None:
        print("Key not found")
    else:
        print(f"Found: {value}")
except Exception as e:
    print(f"Database error: {e}")
```

### In Lua

```python
result = db.execute_lua('''
    local success, err = pcall(function()
        return db:get("some_key")
    end)

    if success then
        return err or "nil"
    else
        return "Error: " .. tostring(err)
    end
''')
```

## Best Practices

1. **Use meaningful key patterns**: `entity:id:attribute` (e.g., `user:123:email`)
2. **Store JSON for complex data**: Serialize objects before storing
3. **Close the database**: Always call `db.close()` when done
4. **Handle None values**: Always check if `get` returns None

## Clean Up

```python
db.close()
```

## Next Steps

- [Using Namespaces](namespaces.md) - Organize data with namespaces
- [Lua Queries](lua-queries.md) - Advanced query patterns
- [Vector Search](vector-search.md) - Semantic search capabilities
