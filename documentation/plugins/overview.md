# Plugins Overview

Liath uses a plugin architecture to provide extensible functionality. Plugins expose functions to Lua queries.

## Built-in Plugins

| Plugin | Name | Description | Extra Required |
|--------|------|-------------|----------------|
| [Database](db.md) | `db` | Core CRUD operations | - |
| [Embeddings](embed.md) | `embed` | Text/image embeddings | `liath[embed]` |
| [Vector DB](vdb.md) | `vdb` | Vector similarity search | `liath[vdb]` |
| [LLM](llm.md) | `llm` | Language model access | `liath[llm]` |
| [File](file.md) | `file` | File read/write | - |
| [Cache](cache.md) | `cache` | Query result caching | - |
| [Backup](backup.md) | `backup` | Backup and restore | - |
| [Monitor](monitor.md) | `monitor` | System monitoring | - |

## Using Plugins in Lua

Plugins are accessed via the `plugins` global:

```lua
-- Access plugin functions
local result = plugins.db.get("key")
local embedding = plugins.embed.embed("text")
local search_results = plugins.vdb.vdb_search("index", vector, 5)
local response = plugins.llm.llm_complete("prompt")
```

## Plugin Availability

Plugins may not be available if their dependencies aren't installed:

```lua
-- Check if plugin is available
if plugins.embed then
    local embedding = plugins.embed.embed("text")
else
    return "Embedding plugin not available"
end
```

## Installing Plugin Dependencies

```bash
# Embeddings
pip install liath[embed]

# Vector database
pip install liath[vdb]

# Language models
pip install liath[llm]

# All AI features
pip install liath[embed,vdb,llm]
```

## Plugin Return Format

Most plugin functions return JSON strings:

```lua
local result = plugins.embed.embed("Hello")
-- Returns: {"status": "success", "embedding": [...]}

-- Parse with cjson if needed
local json = require("cjson")
local data = json.decode(result)
print(data.status)  -- "success"
```

## Custom Plugins

See [Building Plugins](../tutorials/building-plugins.md) to create your own.
