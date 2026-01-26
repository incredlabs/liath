# File Plugin (file)

Read and write files from Lua queries.

## Functions

### plugins.file.file_read(path)

Read a file's contents.

**Parameters:**

- `path` (string): File path to read

**Returns:** JSON with file contents

**Example:**
```lua
local result = plugins.file.file_read("/path/to/file.txt")
-- Returns: {"status": "success", "content": "file contents..."}
```

### plugins.file.file_write(path, content)

Write content to a file.

**Parameters:**

- `path` (string): File path to write
- `content` (string): Content to write

**Returns:** JSON status

**Example:**
```lua
local result = plugins.file.file_write("/path/to/output.txt", "Hello, World!")
-- Returns: {"status": "success", "message": "File written"}
```

### plugins.file.file_delete(path)

Delete a file.

**Parameters:**

- `path` (string): File path to delete

**Returns:** JSON status

**Example:**
```lua
local result = plugins.file.file_delete("/path/to/file.txt")
-- Returns: {"status": "success", "message": "File deleted"}
```

## Usage Examples

### Load Configuration

```lua
local json = require("cjson")

local result = plugins.file.file_read("config.json")
local data = json.decode(result)

if data.status == "success" then
    local config = json.decode(data.content)
    return config.database_name
else
    return "Error: " .. data.message
end
```

### Export Data

```lua
local json = require("cjson")

-- Collect data
local items = db:iterator()
local export_data = {}
for _, item in ipairs(items) do
    for key, value in pairs(item) do
        export_data[key] = value
    end
end

-- Write to file
local content = json.encode(export_data)
plugins.file.file_write("export.json", content)
return "Exported " .. #items .. " items"
```

### Import Data

```lua
local json = require("cjson")

local result = plugins.file.file_read("import.json")
local data = json.decode(result)

if data.status == "success" then
    local import_data = json.decode(data.content)
    local count = 0

    for key, value in pairs(import_data) do
        db:put(key, value)
        count = count + 1
    end

    return "Imported " .. count .. " items"
else
    return "Import failed: " .. data.message
end
```

## Security Considerations

1. **Path validation**: Be careful with user-provided paths
2. **Sandboxing**: Consider restricting accessible directories
3. **Permissions**: Ensure appropriate file permissions
