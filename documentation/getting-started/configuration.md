# Configuration

This guide covers Liath's configuration options and settings.

## Storage Backends

Liath supports two storage backends:

### LevelDB (Default)

LevelDB is a lightweight, fast key-value store. It's the default backend and requires no additional dependencies.

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./data", storage_type="leveldb")
```

**Pros:**

- Lightweight and fast
- No additional system dependencies
- Good for development and smaller datasets

**Cons:**

- Limited concurrent access
- No column family support
- Simpler transaction semantics

### RocksDB

RocksDB is a high-performance storage engine based on LevelDB with additional features.

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./data", storage_type="rocksdb")
```

**Pros:**

- High performance for large datasets
- Column family support
- Better compression
- Advanced tuning options

**Cons:**

- Requires `liath[rocksdb]` extra
- Higher memory usage
- More complex to tune

### Auto Selection

Use `auto` to let Liath choose the best available backend:

```python
db = EmbeddedLiath(data_dir="./data", storage_type="auto")
```

This tries RocksDB first, then falls back to LevelDB.

## Data Directory Structure

Liath organizes data in the following structure:

```
data_dir/
├── default/              # Default namespace
│   ├── db/               # Storage database files
│   └── luarocks/         # Lua modules for this namespace
├── users/                # Custom namespace
│   ├── db/
│   └── luarocks/
├── metadata.json         # Namespace metadata
└── users.json            # User credentials
```

## Plugin Configuration

### Built-in Plugins

Liath loads built-in plugins automatically:

- `db` - Database operations
- `embed` - Embeddings (requires `liath[embed]`)
- `vdb` - Vector database (requires `liath[vdb]`)
- `llm` - Language models (requires `liath[llm]`)
- `file` - File operations
- `cache` - Query caching
- `backup` - Backup/restore
- `monitor` - System monitoring

### Custom Plugins

Load custom plugins from a directory:

```python
from liath import Database

db = Database(
    data_dir="./data",
    plugins_dir="./my_plugins"
)
```

## CLI Configuration

Configure the CLI with command-line arguments:

```bash
liath-cli \
    --storage auto \
    --data-dir ./data \
    --plugins-dir ./my_plugins
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--storage` | `auto` | Storage backend: `auto`, `rocksdb`, `leveldb` |
| `--data-dir` | `./data` | Data directory path |
| `--plugins-dir` | None | Additional plugins directory |

## Server Configuration

Configure the HTTP server:

```bash
liath-server \
    --host 0.0.0.0 \
    --port 5000 \
    --data-dir ./data \
    --storage auto
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `0.0.0.0` | Server bind address |
| `--port` | `5000` | Server port |
| `--data-dir` | `./data` | Data directory path |
| `--storage` | `auto` | Storage backend |

## Environment Variables

Liath respects the following environment variables for LLM integration:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM plugin |

## LuaRocks Integration

Each namespace can have its own Lua modules. Install modules using:

```python
from liath import Database

db = Database(data_dir="./data")
db.install_package("default", "lua-cjson")
```

Or via Lua query:

```lua
-- From within a Lua query (if package installer is exposed)
return "Package installation should be done via Python API"
```
