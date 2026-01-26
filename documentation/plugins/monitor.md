# Monitoring Plugin (monitor)

System monitoring and logging capabilities.

## Functions

### plugins.monitor.monitor_log(level, message)

Write a log entry.

**Parameters:**

- `level` (string): Log level (`debug`, `info`, `warning`, `error`, `critical`)
- `message` (string): Log message

**Returns:** JSON status

**Example:**
```lua
plugins.monitor.monitor_log("info", "Query executed successfully")
plugins.monitor.monitor_log("error", "Failed to connect to external service")
```

### plugins.monitor.monitor_get_stats()

Get system statistics.

**Returns:** JSON with system metrics

**Example:**
```lua
local result = plugins.monitor.monitor_get_stats()
-- Returns:
-- {
--     "uptime": 3600,
--     "query_count": 1500,
--     "error_count": 5,
--     "cpu_usage": "25%",
--     "memory_usage": "45%",
--     "disk_usage": "60%",
--     "active_threads": 4
-- }
```

### plugins.monitor.monitor_get_log_tail(lines)

Get recent log entries.

**Parameters:**

- `lines` (number, optional): Number of lines to retrieve (default: 50)

**Returns:** JSON with log entries

**Example:**
```lua
local result = plugins.monitor.monitor_get_log_tail(100)
-- Returns: {"status": "success", "logs": ["2024-01-15 10:30:00 - INFO - ...", ...]}
```

## Usage Examples

### Application Logging

```lua
local json = require("cjson")

local function log_operation(operation, details)
    local message = operation .. ": " .. json.encode(details)
    plugins.monitor.monitor_log("info", message)
end

-- Log a user action
log_operation("user_login", {user_id = "123", ip = "192.168.1.1"})

-- Log an error
plugins.monitor.monitor_log("error", "Database connection timeout")

return "Logged"
```

### Health Check

```lua
local json = require("cjson")

local function health_check()
    local stats = json.decode(plugins.monitor.monitor_get_stats())

    local health = {
        status = "healthy",
        checks = {}
    }

    -- Check CPU
    local cpu = tonumber(stats.cpu_usage:match("(%d+)"))
    if cpu > 80 then
        health.status = "degraded"
        table.insert(health.checks, {name = "cpu", status = "warning", value = stats.cpu_usage})
    else
        table.insert(health.checks, {name = "cpu", status = "ok", value = stats.cpu_usage})
    end

    -- Check memory
    local memory = tonumber(stats.memory_usage:match("(%d+)"))
    if memory > 90 then
        health.status = "critical"
        table.insert(health.checks, {name = "memory", status = "critical", value = stats.memory_usage})
    elseif memory > 80 then
        health.status = "degraded"
        table.insert(health.checks, {name = "memory", status = "warning", value = stats.memory_usage})
    else
        table.insert(health.checks, {name = "memory", status = "ok", value = stats.memory_usage})
    end

    -- Check error rate
    local error_rate = stats.error_count / math.max(stats.query_count, 1)
    if error_rate > 0.05 then
        health.status = "degraded"
        table.insert(health.checks, {name = "errors", status = "warning", value = string.format("%.2f%%", error_rate * 100)})
    else
        table.insert(health.checks, {name = "errors", status = "ok", value = string.format("%.2f%%", error_rate * 100)})
    end

    return json.encode(health)
end

return health_check()
```

### Performance Monitoring

```lua
local json = require("cjson")

local function time_operation(name, operation_fn)
    local start = os.clock()
    local result = operation_fn()
    local elapsed = os.clock() - start

    plugins.monitor.monitor_log("info",
        string.format("Operation '%s' completed in %.4f seconds", name, elapsed))

    return result
end

-- Time a database operation
local result = time_operation("full_scan", function()
    local items = db:iterator()
    return #items
end)

return "Found " .. result .. " items"
```

### Error Tracking

```lua
local json = require("cjson")

local function safe_execute(operation_name, fn)
    local success, result = pcall(fn)

    if success then
        plugins.monitor.monitor_log("debug", operation_name .. " succeeded")
        return result
    else
        plugins.monitor.monitor_log("error",
            operation_name .. " failed: " .. tostring(result))
        return nil, result
    end
end

local result, err = safe_execute("data_import", function()
    -- Potentially failing operation
    return db:get("nonexistent")
end)

if err then
    return "Error: " .. err
else
    return result or "No data"
end
```

## Log Levels

| Level | Use Case |
|-------|----------|
| `debug` | Detailed diagnostic information |
| `info` | General operational messages |
| `warning` | Potential issues that aren't errors |
| `error` | Error conditions |
| `critical` | Severe errors requiring immediate attention |

## Best Practices

1. **Use appropriate levels**: Don't log everything as error
2. **Include context**: Add relevant IDs and values to messages
3. **Monitor trends**: Track metrics over time
4. **Set alerts**: Monitor for critical thresholds
5. **Log rotation**: Implement log file rotation
