# Architecture

This document describes Liath's system architecture and design decisions.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  EmbeddedLiath  │   DatabaseCLI   │        HTTP Server          │
│  (Python API)   │     (CLI)       │       (REST API)            │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         └─────────────────┼───────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Database Class                            │
│  - Namespace management                                         │
│  - Plugin orchestration                                         │
│  - Lua runtime management                                       │
│  - User authentication                                          │
└─────────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Lua Runtime    │ │   Plugins   │ │ Storage Backend │
│  (Lupa/LuaJIT)  │ │  (db, vdb,  │ │ (RocksDB or     │
│                 │ │  embed...)  │ │  LevelDB)       │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

## Core Components

### Database Class

The `Database` class (`liath/database.py`) is the central orchestrator:

- **Namespace Management**: Creates and manages isolated data namespaces
- **Plugin Loading**: Discovers and loads plugins from directories
- **Query Execution**: Sets up Lua runtime and executes queries
- **User Management**: Handles authentication with hashed passwords

### EmbeddedLiath

A simplified interface (`liath/embedded.py`) for common operations:

- Wraps `Database` class
- Provides `put`, `get`, `delete` methods
- Handles namespace switching
- Exposes `execute_lua` for advanced queries

### Storage Backends

Abstract base class with two implementations:

**StorageBase** (`liath/storage/base.py`):
- Defines interface for storage operations
- Methods: `get`, `put`, `delete`, `iterator`, `write_batch`

**RocksDBStorage** (`liath/storage/rocksdb_storage.py`):
- High-performance storage
- Column families
- Transactions
- Compression

**LevelDBStorage** (`liath/storage/leveldb_storage.py`):
- Lightweight storage
- Simpler implementation
- Good for development

## Plugin System

### Plugin Architecture

```
┌─────────────────────────────────────────┐
│               PluginBase                │
│  - initialize(context)                  │
│  - get_lua_interface() -> dict          │
│  - name property                        │
│  - lua_callable decorator               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │DBPlugin │ │EmbedPlug│ │VDBPlugin│ ...
   └─────────┘ └─────────┘ └─────────┘
```

### Plugin Loading Flow

1. `Database.load_plugins()` scans plugin directories
2. Python modules are imported dynamically
3. Classes inheriting from `PluginBase` are instantiated
4. During query execution, `initialize(context)` is called
5. `get_lua_interface()` returns functions for Lua

### Plugin Context

Plugins receive a context dictionary:

```python
{
    'namespace': 'default',
    'db': <StorageBase instance>,
    'data_dir': '/path/to/data',
    'packages': '/path/to/luarocks'
}
```

## Query Execution Flow

```
User Query
    │
    ▼
Database.execute_query(namespace, query)
    │
    ├─► Acquire namespace lock
    │
    ├─► Create Lua runtime (lupa)
    │
    ├─► Configure Lua paths
    │
    ├─► Initialize plugins for namespace
    │
    ├─► Set Lua globals:
    │       - db: storage interface
    │       - plugins: plugin functions
    │
    ├─► Wrap query in function
    │
    ├─► Execute Lua code
    │
    ├─► Convert Lua result to Python
    │
    ├─► Release namespace lock
    │
    └─► Return formatted result
```

## Namespace Isolation

Each namespace has:

- **Separate storage**: Independent database files
- **Own Lua context**: Isolated execution environment
- **Plugin instances**: Fresh initialization per namespace
- **LuaRocks tree**: Namespace-specific Lua modules
- **Thread lock**: Prevents concurrent access conflicts

## Data Flow

### Write Operation

```
db.put("key", "value")
    │
    ▼
EmbeddedLiath.put()
    │
    ▼
Database.execute_query("default", 'db:put("key", "value")')
    │
    ▼
Lua runtime executes
    │
    ▼
DBPlugin.put() called via Lua interface
    │
    ▼
StorageBase.put()
    │
    ▼
RocksDB/LevelDB write
```

### Read Operation

```
db.get("key")
    │
    ▼
EmbeddedLiath.get()
    │
    ▼
Database.execute_query("default", 'return db:get("key")')
    │
    ▼
Lua runtime executes
    │
    ▼
DBPlugin.get() called
    │
    ▼
StorageBase.get()
    │
    ▼
RocksDB/LevelDB read
    │
    ▼
Result converted to Python
```

## Thread Safety

- **Namespace locks**: Each namespace has a threading lock
- **Plugin state**: Plugins should manage their own thread safety
- **Storage backends**: Underlying databases handle concurrency

## Directory Structure

```
data_dir/
├── default/                 # Namespace
│   ├── db/                  # Storage files
│   │   ├── LOCK
│   │   ├── CURRENT
│   │   ├── MANIFEST-*
│   │   └── *.sst           # Data files
│   └── luarocks/           # Lua modules
│       └── ...
├── users/                   # Another namespace
│   ├── db/
│   └── luarocks/
├── metadata.json           # Namespace metadata
└── users.json              # User credentials
```

## Design Decisions

### Why Lua?

- Sandboxed execution environment
- Lightweight and fast (LuaJIT compatible)
- Easy to embed (via lupa)
- Expressive for data manipulation
- Plugin functions naturally become Lua functions

### Why Pluggable Storage?

- Different use cases need different trade-offs
- RocksDB for production, LevelDB for development
- Easy to add new backends

### Why Namespace Isolation?

- Multi-tenant support
- Data organization
- Environment separation (dev/prod)
- Security boundaries
