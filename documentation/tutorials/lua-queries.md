# Lua Queries

Liath uses Lua as its query language, giving you a full programming environment for data operations.

## Why Lua?

- **Expressive**: Write complex logic naturally
- **Sandboxed**: Safe execution environment
- **Extensible**: Plugins add functions to Lua
- **Fast**: LuaJIT-compatible for high performance

## Basic Syntax

Execute Lua code with `execute_lua`:

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./data")

# Simple return
result = db.execute_lua('return "Hello, Lua!"')
print(result)  # Output: Hello, Lua!
```

## The `db` Object

The `db` global provides database access:

```python
# Get a value
result = db.execute_lua('return db:get("key")')

# Put a value
db.execute_lua('db:put("key", "value")')

# Delete a value
db.execute_lua('db:delete("key")')
```

## Variables and Types

```python
# Numbers
result = db.execute_lua('''
    local x = 10
    local y = 3.14
    return x + y
''')
print(result)  # Output: 13.14

# Strings
result = db.execute_lua('''
    local name = "Alice"
    return "Hello, " .. name .. "!"
''')
print(result)  # Output: Hello, Alice!

# Tables (arrays)
result = db.execute_lua('''
    local fruits = {"apple", "banana", "cherry"}
    return fruits
''')
print(result)  # Output: ['apple', 'banana', 'cherry']

# Tables (dictionaries)
result = db.execute_lua('''
    local user = {
        name = "Alice",
        age = 30,
        active = true
    }
    return user
''')
print(result)  # Output: {'name': 'Alice', 'age': 30, 'active': True}
```

## Control Flow

### Conditionals

```python
result = db.execute_lua('''
    local value = db:get("score")
    local score = tonumber(value) or 0

    if score >= 90 then
        return "A"
    elseif score >= 80 then
        return "B"
    elseif score >= 70 then
        return "C"
    else
        return "F"
    end
''')
```

### Loops

```python
# For loop
result = db.execute_lua('''
    local sum = 0
    for i = 1, 10 do
        sum = sum + i
    end
    return sum
''')
print(result)  # Output: 55

# While loop
result = db.execute_lua('''
    local i = 1
    while i <= 5 do
        db:put("item:" .. i, "Value " .. i)
        i = i + 1
    end
    return "Stored 5 items"
''')

# Iterate over table
result = db.execute_lua('''
    local items = db:iterator()
    local count = 0
    for _, item in ipairs(items) do
        count = count + 1
    end
    return count
''')
```

## Functions

```python
result = db.execute_lua('''
    -- Define a function
    local function greet(name)
        return "Hello, " .. name .. "!"
    end

    -- Call it
    return greet("World")
''')
print(result)  # Output: Hello, World!
```

## Working with JSON

Store and retrieve structured data:

```python
# Store JSON
db.execute_lua('''
    local json = require("cjson")  -- If installed via LuaRocks
    local user = {name = "Alice", age = 30}
    db:put("user:1", json.encode(user))
''')

# Or use string formatting
db.execute_lua('''
    local user_json = '{"name": "Alice", "age": 30}'
    db:put("user:1", user_json)
''')
```

## Using Plugins

Access plugins via the `plugins` global:

```python
# Embedding text (requires liath[embed])
result = db.execute_lua('''
    local embedding = plugins.embed.embed("Hello, world!")
    return embedding
''')

# Vector search (requires liath[vdb])
result = db.execute_lua('''
    plugins.vdb.vdb_create_index("my_index", 384)
    plugins.vdb.vdb_add("my_index", "doc1", {0.1, 0.2, 0.3, ...})
    local results = plugins.vdb.vdb_search("my_index", {0.1, 0.2, 0.3, ...}, 5)
    return results
''')

# LLM completion (requires liath[llm])
result = db.execute_lua('''
    local response = plugins.llm.llm_complete("What is 2+2?")
    return response
''')
```

## Error Handling

```python
result = db.execute_lua('''
    local success, result = pcall(function()
        -- Code that might fail
        return db:get("key")
    end)

    if success then
        return result or "nil"
    else
        return "Error: " .. tostring(result)
    end
''')
```

## Multi-line Queries

For complex queries, use multi-line strings:

```python
query = '''
    -- Find all users with high scores
    local items = db:iterator()
    local high_scorers = {}

    for _, item in ipairs(items) do
        for key, value in pairs(item) do
            if key:match("^user:") then
                local data = require("cjson").decode(value)
                if data.score and data.score > 90 then
                    table.insert(high_scorers, data)
                end
            end
        end
    end

    return high_scorers
'''
result = db.execute_lua(query)
```

## Output Formats

Liath can return results in different formats:

```python
from liath import Database

db = Database(data_dir="./data")

# Dictionary (default)
result = db.execute_query("default", "return {a=1, b=2}", "dict")

# JSON string
result = db.execute_query("default", "return {a=1, b=2}", "json")

# YAML string
result = db.execute_query("default", "return {a=1, b=2}", "yaml")
```

## Performance Tips

1. **Minimize iterations**: Filter data in Lua, not Python
2. **Batch operations**: Use `write_batch` for multiple writes
3. **Cache frequently accessed data**: Use the cache plugin
4. **Avoid deep nesting**: Keep table structures simple

## Common Patterns

### Counter

```python
db.execute_lua('''
    local current = tonumber(db:get("counter")) or 0
    db:put("counter", tostring(current + 1))
    return current + 1
''')
```

### Key Prefix Search

```python
result = db.execute_lua('''
    local items = db:iterator()
    local matches = {}

    for _, item in ipairs(items) do
        for key, value in pairs(item) do
            if key:sub(1, 5) == "user:" then
                matches[key] = value
            end
        end
    end

    return matches
''')
```

## Clean Up

```python
db.close()
```

## Next Steps

- [Vector Search](vector-search.md) - Semantic search with embeddings
- [Plugin Documentation](../plugins/overview.md) - All available plugins
