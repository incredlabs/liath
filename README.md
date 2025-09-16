# Liath

Liath is a programmable key–value database with Lua as its query language and a pluggable architecture for storage and extensions. It supports RocksDB and LevelDB backends, a plugin system (vector search, embeddings, LLMs, files, caching, monitoring, backup), and both CLI and HTTP interfaces.

[PyPI](https://pypi.org/project/liath/) • [License: MIT](LICENSE)

## Features

- Storage backends: RocksDB, LevelDB
- Lua query execution via `lupa`
- Plugin system (vector DB, embeddings, LLM, files, caching, monitoring, backup)
- Namespaces with per-namespace LuaRocks module trees
- CLI and HTTP server

For details, see docs/features.md.

## Installation

Using pip:
```bash
pip install liath
```

Optional extras:
- LLM: `pip install liath[llm]`
- Embeddings: `pip install liath[embed]`
- Vector DB: `pip install liath[vdb]`

From source with Poetry:
```bash
git clone https://github.com/nudgelang/liath.git
cd liath
poetry install
```

Create directories used by LuaRocks per namespace:
```bash
mkdir -p data/namespaces/default/{share/lua,lib/lua} plugins
```

Install common LuaRocks packages (optional):
```bash
./liath/setup_luarocks.sh
```

## Usage

Embedded (Python):
```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./my_data", storage_type="auto")
db.put("key", "value")
print(db.get("key"))
print(db.execute_lua('return db:get("key")'))
db.set_namespace("my_ns")
db.close()
```

CLI:
```bash
liath-cli --storage auto
```

Server:
```bash
liath-server --storage auto --host 0.0.0.0 --port 5000
```

### LuaRocks modules

Liath searches for Lua modules in:
- User tree: `~/.luarocks`
- Namespace tree: `./data/namespaces/<namespace>/{share,lib}/lua/<version>`

Install into a namespace tree:
```bash
luarocks install --tree=./data/namespaces/<namespace> package_name
```

Use in queries:
```lua
local json = require("cjson")
return json.encode({key = "value"})
```

## Extending with Plugins

Create a plugin by subclassing `liath.plugin_base.PluginBase` and returning a Lua interface (a table of functions) from `get_lua_interface()`. Place plugins in your own directory and point `Database(..., plugins_dir=...)` to it, or use the packaged plugins under `liath/plugins`.

## Documentation

- Features: docs/features.md
- Roadmap/TODO: docs/todo.md
- Assessment: docs/assessment.md
- Package notes: docs/library-transformation.md

## Case Studies: AI Agents and Workflows

- Retrieval-augmented answering (RAG)
  - Ingest: embed text and add to a vector index.
  - Retrieve: search similar items by query embedding.
  - Generate: call an LLM with retrieved context.
  - Example (Lua, assumes `embed`, `vdb`, and `llm` plugins available):
    ```lua
    -- 1) Ensure index exists
    if not plugins.vdb then return { error = 'vdb plugin not available' } end
    plugins.vdb.vdb_create_index(384)  -- dims depend on model

    -- 2) Add a document
    local doc_id, text = 'doc:1', 'Streaming databases support high-ingest analytics.'
    local e = plugins.embed.embed(text)  -- returns JSON; keep simple for illustration
    -- store original text alongside
    db:put(doc_id, text)
    -- add vector to index (assumes you decode to a Lua table in your flow)
    -- plugins.vdb.vdb_add(doc_id, embedding)

    -- 3) Query
    local q = 'How do streaming DBs handle ingestion?'
    local qe = plugins.embed.embed(q)
    -- local matches = plugins.vdb.vdb_search(qe, 3)  -- returns nearest IDs

    -- 4) Construct a prompt from retrieved docs and ask the LLM
    -- local ctx = db:get('doc:1')
    -- return plugins.llm.llm_chat({ {role='user', content='Use context: '..ctx..'\nQuestion: '..q } })
    return 'RAG pipeline outline complete'
    ```

- Tool-using agent (files + key–value + HTTP)
  - The agent reads input files, stores metadata in the KV store, optionally calls HTTP, and writes results.
  - Example (Lua):
    ```lua
    if not plugins.file then return { error = 'file plugin not available' } end
    local content = plugins.file.file_read('notes/todo.txt') or ''
    db:put('last_todo', content)
    -- Optional HTTP call via LuaSocket (installed via LuaRocks)
    -- local http = require('socket.http')
    -- local body, code = http.request('https://example.com/api')
    plugins.file.file_write('notes/summary.txt', 'Synced. Length: '..#content)
    return { ok = true }
    ```

- Batch embedding workflow
  - Periodically embed new items and update the vector index; simple job orchestration can be done from Python.
  - Example (Python):
    ```python
    from liath import EmbeddedLiath
    db = EmbeddedLiath(data_dir='./data', storage_type='auto')
    db.set_namespace('prod')

    items = [
        ('doc:2', 'Liath provides a Lua-based query surface.'),
        ('doc:3', 'LevelDB is a lightweight KV store.'),
    ]
    for k, v in items:
        db.put(k, v)
        db.execute_lua(f"plugins.embed.embed('{v}')")  # embed, then add to index in your flow
    db.execute_lua("plugins.vdb.vdb_create_index(384)")
    # db.execute_lua("plugins.vdb.vdb_add('doc:2', <vector>)")
    db.close()
    ```

## Contributing

Issues and pull requests are welcome.

## License

MIT — see LICENSE.
