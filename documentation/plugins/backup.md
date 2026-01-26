# Backup Plugin (backup)

Backup and restore database data.

## Functions

### plugins.backup.backup_create(path)

Create a backup of the current namespace.

**Parameters:**

- `path` (string): Path to save the backup

**Returns:** JSON status

**Example:**
```lua
local result = plugins.backup.backup_create("/backups/daily_backup.json")
-- Returns: {"status": "success", "message": "Backup created", "count": 1000}
```

### plugins.backup.backup_restore(path)

Restore data from a backup.

**Parameters:**

- `path` (string): Path to the backup file

**Returns:** JSON status

**Example:**
```lua
local result = plugins.backup.backup_restore("/backups/daily_backup.json")
-- Returns: {"status": "success", "message": "Restored", "count": 1000}
```

### plugins.backup.backup_list(directory)

List available backups in a directory.

**Parameters:**

- `directory` (string): Directory to scan

**Returns:** JSON with backup files

**Example:**
```lua
local result = plugins.backup.backup_list("/backups")
-- Returns: {"status": "success", "backups": ["backup1.json", "backup2.json"]}
```

## Usage Examples

### Scheduled Backup

```lua
local json = require("cjson")

local function create_timestamped_backup()
    local timestamp = os.date("%Y%m%d_%H%M%S")
    local path = "/backups/backup_" .. timestamp .. ".json"

    local result = plugins.backup.backup_create(path)
    local data = json.decode(result)

    if data.status == "success" then
        return "Backup created: " .. path .. " (" .. data.count .. " items)"
    else
        return "Backup failed: " .. data.message
    end
end

return create_timestamped_backup()
```

### Restore with Confirmation

```lua
local json = require("cjson")

local function restore_backup(backup_path)
    -- Check current data count
    local items = db:iterator()
    local current_count = #items

    if current_count > 0 then
        return "Warning: Database has " .. current_count .. " items. Clear first or proceed with caution."
    end

    local result = plugins.backup.backup_restore(backup_path)
    local data = json.decode(result)

    if data.status == "success" then
        return "Restored " .. data.count .. " items"
    else
        return "Restore failed: " .. data.message
    end
end

return restore_backup("/backups/backup_20240115.json")
```

### Backup Rotation

```lua
local json = require("cjson")

local function rotate_backups(backup_dir, keep_count)
    -- List existing backups
    local list_result = plugins.backup.backup_list(backup_dir)
    local list_data = json.decode(list_result)

    if list_data.status ~= "success" then
        return "Failed to list backups"
    end

    local backups = list_data.backups or {}
    table.sort(backups)  -- Sort by name (assumes timestamped names)

    -- Delete old backups
    local deleted = 0
    while #backups > keep_count do
        local oldest = table.remove(backups, 1)
        plugins.file.file_delete(backup_dir .. "/" .. oldest)
        deleted = deleted + 1
    end

    -- Create new backup
    local timestamp = os.date("%Y%m%d_%H%M%S")
    local new_path = backup_dir .. "/backup_" .. timestamp .. ".json"
    plugins.backup.backup_create(new_path)

    return "Created new backup, deleted " .. deleted .. " old backups"
end

return rotate_backups("/backups", 7)  -- Keep last 7 backups
```

## Backup Format

Backups are stored as JSON:

```json
{
    "metadata": {
        "namespace": "default",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "0.1.0"
    },
    "data": {
        "key1": "value1",
        "key2": "value2"
    }
}
```

## Best Practices

1. **Regular backups**: Schedule automatic backups
2. **Test restores**: Periodically verify backups work
3. **Offsite storage**: Copy backups to external storage
4. **Rotation**: Implement retention policies
5. **Compression**: Consider compressing large backups
