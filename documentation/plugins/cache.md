# Cache Plugin (cache)

Cache query results for improved performance.

## Functions

### plugins.cache.cache_get(key)

Retrieve a cached value.

**Parameters:**

- `key` (string): Cache key

**Returns:** JSON with cached value or null

**Example:**
```lua
local result = plugins.cache.cache_get("expensive_query")
-- Returns: {"status": "success", "value": "cached data"} or {"status": "success", "value": null}
```

### plugins.cache.cache_set(key, value, ttl)

Store a value in cache.

**Parameters:**

- `key` (string): Cache key
- `value` (string): Value to cache
- `ttl` (number, optional): Time-to-live in seconds

**Returns:** JSON status

**Example:**
```lua
plugins.cache.cache_set("query_result", "data", 3600)  -- Cache for 1 hour
-- Returns: {"status": "success", "message": "Cached"}
```

### plugins.cache.cache_delete(key)

Remove a cached value.

**Parameters:**

- `key` (string): Cache key

**Returns:** JSON status

**Example:**
```lua
plugins.cache.cache_delete("stale_data")
-- Returns: {"status": "success", "message": "Deleted"}
```

### plugins.cache.cache_clear()

Clear all cached values.

**Returns:** JSON status

**Example:**
```lua
plugins.cache.cache_clear()
-- Returns: {"status": "success", "message": "Cache cleared"}
```

## Usage Examples

### Cache-Aside Pattern

```lua
local json = require("cjson")

local function get_user(user_id)
    local cache_key = "user:" .. user_id

    -- Try cache first
    local cached = json.decode(plugins.cache.cache_get(cache_key))
    if cached.value then
        return cached.value
    end

    -- Fetch from database
    local user = db:get("user:" .. user_id)

    -- Cache the result
    if user then
        plugins.cache.cache_set(cache_key, user, 300)  -- 5 minutes
    end

    return user
end

return get_user("123")
```

### Memoize Expensive Operations

```lua
local json = require("cjson")

local function expensive_computation(input)
    local cache_key = "compute:" .. input

    local cached = json.decode(plugins.cache.cache_get(cache_key))
    if cached.value then
        return json.decode(cached.value)
    end

    -- Expensive operation
    local result = {}
    local items = db:iterator()
    for _, item in ipairs(items) do
        for key, value in pairs(item) do
            if key:match(input) then
                table.insert(result, {key = key, value = value})
            end
        end
    end

    -- Cache result
    plugins.cache.cache_set(cache_key, json.encode(result), 600)

    return result
end

return expensive_computation("user:")
```

### Invalidation on Update

```lua
local json = require("cjson")

local function update_user(user_id, data)
    -- Update database
    db:put("user:" .. user_id, json.encode(data))

    -- Invalidate cache
    plugins.cache.cache_delete("user:" .. user_id)
    plugins.cache.cache_delete("users:list")  -- Invalidate related caches

    return "Updated"
end

return update_user("123", {name = "Alice", email = "alice@example.com"})
```

## Best Practices

1. **Choose appropriate TTL**: Balance freshness vs. performance
2. **Use consistent keys**: Establish naming conventions
3. **Handle cache misses**: Always have fallback logic
4. **Invalidate on writes**: Clear cache when data changes
5. **Don't cache everything**: Cache expensive or frequently accessed data
