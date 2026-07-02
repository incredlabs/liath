# Liath

**The SQLite for AI agents.** Programmable memory that agents query with sandboxed Lua — key-value storage, embeddings, and vector search in a single Python dependency. Store data, run queries, and build AI workflows without standing up a server.

[![PyPI version](https://img.shields.io/pypi/v/liath.svg)](https://pypi.org/project/liath/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://docs.incredlabs.com/liath)

**[Website](https://liath.incredlabs.com) · [Documentation](https://docs.incredlabs.com/liath) · [ORMDB (sibling project)](https://ormdb.incredlabs.com)**

> Also available as a Rust crate: [**liath-rs**](https://github.com/incredlabs/liath-rs).

---

## Why Liath?

- **Lua as your query language** — Write expressive queries with a real programming language
- **Pluggable AI capabilities** — Embeddings, vector search, and LLM integration built-in
- **Simple Python API** — Get started in 3 lines of code
- **Multiple storage backends** — RocksDB for production, LevelDB for development
- **Namespace isolation** — Multi-tenant ready with isolated data contexts

## Quick Start

### Install

```bash
pip install liath
```

### Use

```python
from liath import EmbeddedLiath

# Initialize
db = EmbeddedLiath(data_dir="./data")

# Store and retrieve
db.put("user:1", '{"name": "Alice", "role": "admin"}')
print(db.get("user:1"))

# Run Lua queries
result = db.execute_lua('''
    local user = db:get("user:1")
    return "Found: " .. user
''')

db.close()
```

**That's it.** You have a working database with Lua queries.

## Installation Options

```bash
# Core (LevelDB storage)
pip install liath

# With AI features
pip install liath[embed]      # Text embeddings (FastEmbed)
pip install liath[vdb]        # Vector search (USearch)
pip install liath[llm]        # LLM access (OpenAI, Llama)

# All features
pip install liath[embed,vdb,llm]

# High-performance storage
pip install liath[rocksdb]
```

## Core Concepts

### 1. Key-Value Storage

```python
db.put("key", "value")
value = db.get("key")
db.delete("key")
```

### 2. Lua Queries

Access the `db` object and `plugins` from Lua:

```python
db.execute_lua('''
    -- Store data
    db:put("counter", "0")

    -- Read and modify
    local count = tonumber(db:get("counter"))
    db:put("counter", tostring(count + 1))

    return db:get("counter")
''')
```

### 3. Namespaces

Isolate data for multi-tenant apps or environments:

```python
db.create_namespace("production")
db.set_namespace("production")
db.put("config", '{"debug": false}')

db.set_namespace("development")
db.put("config", '{"debug": true}')  # Separate from production
```

### 4. Plugins

Built-in plugins extend Lua with powerful capabilities:

| Plugin | Function | Install |
|--------|----------|---------|
| `db` | Core CRUD operations | Included |
| `embed` | Text/image embeddings | `liath[embed]` |
| `vdb` | Vector similarity search | `liath[vdb]` |
| `llm` | LLM completions/chat | `liath[llm]` |
| `file` | File read/write | Included |
| `cache` | Query result caching | Included |
| `backup` | Backup/restore | Included |
| `monitor` | System monitoring | Included |

## Example: RAG Pipeline

Build retrieval-augmented generation in ~20 lines:

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./rag_data")

# Index documents
db.execute_lua('''
    local json = require("cjson")

    -- Create vector index
    plugins.vdb.vdb_create_index("docs", 384)

    -- Add a document
    local text = "Liath is a programmable database with Lua queries."
    db:put("doc:1", text)

    local emb = json.decode(plugins.embed.embed(text)).embedding
    plugins.vdb.vdb_add("docs", "doc:1", emb)

    return "Indexed"
''')

# Search and generate
answer = db.execute_lua('''
    local json = require("cjson")
    local query = "What is Liath?"

    -- Find similar docs
    local q_emb = json.decode(plugins.embed.embed(query)).embedding
    local results = json.decode(plugins.vdb.vdb_search("docs", q_emb, 3))

    -- Get context
    local context = db:get("doc:" .. results.results[1].id)

    -- Generate answer
    local prompt = "Context: " .. context .. "\\n\\nQuestion: " .. query
    return plugins.llm.llm_complete(prompt)
''')

db.close()
```

## CLI & HTTP Server

### Command Line

```bash
liath-cli --data-dir ./data

# Commands:
# > login admin password
# > use production
# > query return db:get("key")
# > exit
```

### HTTP API

```bash
liath-server --host 0.0.0.0 --port 5000 --data-dir ./data
```

```bash
# Execute queries via HTTP
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "default", "query": "return db:get(\"key\")"}'
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `data_dir` | `./data` | Where to store database files |
| `storage_type` | `auto` | `auto`, `rocksdb`, or `leveldb` |
| `plugins_dir` | None | Path to custom plugins |

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(
    data_dir="/var/lib/liath",
    storage_type="rocksdb"  # Use RocksDB for production
)
```

## Writing Custom Plugins

```python
from liath.plugin_base import PluginBase
import json

class GreetPlugin(PluginBase):
    def initialize(self, context):
        self.db = context.get('db')

    def get_lua_interface(self):
        return {
            'greet_hello': self.lua_callable(self.hello)
        }

    @property
    def name(self):
        return "greet"

    def hello(self, name):
        return json.dumps({"message": f"Hello, {name}!"})
```

Load with: `Database(data_dir="./data", plugins_dir="./my_plugins")`

## Documentation

Full documentation available at the [documentation site](https://docs.incredlabs.com/liath):

- [Installation Guide](https://docs.incredlabs.com/liath/getting-started/installation/)
- [Quick Start Tutorial](https://docs.incredlabs.com/liath/getting-started/quickstart/)
- [Lua Query Guide](https://docs.incredlabs.com/liath/tutorials/lua-queries/)
- [Plugin Reference](https://docs.incredlabs.com/liath/plugins/overview/)
- [API Reference](https://docs.incredlabs.com/liath/reference/api/)

## Contributing

Contributions welcome! See [CONTRIBUTING](https://docs.incredlabs.com/liath/development/contributing/) for guidelines.

```bash
# Development setup
git clone https://github.com/incredlabs/liath.git
cd liath
poetry install --with docs
poetry run pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Part of the [incredlabs](https://www.incredlabs.com) data platform** — Rust-native infrastructure for AI.

- **Liath** — the SQLite for AI agents · [liath.incredlabs.com](https://liath.incredlabs.com) · Rust crate: [liath-rs](https://github.com/incredlabs/liath-rs)
- **ORMDB** — the database that speaks ORM natively · [ormdb.incredlabs.com](https://ormdb.incredlabs.com) · [GitHub](https://github.com/incredlabs/ormdb)
- Website: [www.incredlabs.com](https://www.incredlabs.com) · Contact: [contact@incredlabs.com](mailto:contact@incredlabs.com)
