# Vector Database Plugin (vdb)

Perform vector similarity search using USearch.

## Installation

```bash
pip install liath[vdb]
```

## Functions

### plugins.vdb.vdb_create_index(name, dimensions)

Create a vector index.

**Parameters:**

- `name` (string): Index name
- `dimensions` (number): Vector dimension (must match embedding dimension)

**Returns:** JSON status

**Example:**
```lua
local result = plugins.vdb.vdb_create_index("documents", 384)
-- Returns: {"status": "success", "message": "Index created"}
```

### plugins.vdb.vdb_add(index_name, id, vector)

Add a vector to an index.

**Parameters:**

- `index_name` (string): Index name
- `id` (string): Unique identifier for the vector
- `vector` (table): Array of numbers (embedding)

**Returns:** JSON status

**Example:**
```lua
local json = require("cjson")
local embedding = json.decode(plugins.embed.embed("text")).embedding
plugins.vdb.vdb_add("documents", "doc1", embedding)
```

### plugins.vdb.vdb_search(index_name, vector, k)

Search for similar vectors.

**Parameters:**

- `index_name` (string): Index name
- `vector` (table): Query vector
- `k` (number): Number of results to return

**Returns:** JSON with search results

**Example:**
```lua
local json = require("cjson")
local query_embedding = json.decode(plugins.embed.embed("query text")).embedding
local results = plugins.vdb.vdb_search("documents", query_embedding, 5)
-- Returns: {"status": "success", "results": [{"id": "doc1", "score": 0.95}, ...]}
```

### plugins.vdb.vdb_remove(index_name, id)

Remove a vector from an index.

**Parameters:**

- `index_name` (string): Index name
- `id` (string): Vector identifier

**Returns:** JSON status

**Example:**
```lua
plugins.vdb.vdb_remove("documents", "doc1")
```

### plugins.vdb.vdb_list_indexes()

List all vector indexes.

**Returns:** JSON with index names

**Example:**
```lua
local result = plugins.vdb.vdb_list_indexes()
-- Returns: {"status": "success", "indexes": ["documents", "images"]}
```

### plugins.vdb.vdb_info(index_name)

Get information about an index.

**Parameters:**

- `index_name` (string): Index name

**Returns:** JSON with index metadata

**Example:**
```lua
local result = plugins.vdb.vdb_info("documents")
-- Returns: {"status": "success", "dimensions": 384, "count": 100}
```

## Usage Examples

### Complete RAG Setup

```lua
local json = require("cjson")

-- 1. Create index
plugins.vdb.vdb_create_index("kb", 384)

-- 2. Index documents
local docs = {
    {id = "1", text = "Python is a programming language."},
    {id = "2", text = "Machine learning uses data to learn patterns."},
    {id = "3", text = "Neural networks are inspired by the brain."}
}

for _, doc in ipairs(docs) do
    -- Store text
    db:put("doc:" .. doc.id, doc.text)

    -- Generate and store embedding
    local emb = json.decode(plugins.embed.embed(doc.text)).embedding
    plugins.vdb.vdb_add("kb", doc.id, emb)
end

-- 3. Search
local query = "What programming languages are popular?"
local query_emb = json.decode(plugins.embed.embed(query)).embedding
local results = plugins.vdb.vdb_search("kb", query_emb, 2)

return results
```

### Semantic Search Function

```lua
local json = require("cjson")

local function semantic_search(index_name, query_text, top_k)
    -- Generate query embedding
    local query_result = plugins.embed.embed(query_text)
    local query_emb = json.decode(query_result).embedding

    -- Search index
    local search_result = plugins.vdb.vdb_search(index_name, query_emb, top_k)
    local search_data = json.decode(search_result)

    -- Retrieve documents
    local documents = {}
    for _, result in ipairs(search_data.results or {}) do
        local doc_text = db:get("doc:" .. result.id)
        table.insert(documents, {
            id = result.id,
            score = result.score,
            text = doc_text
        })
    end

    return documents
end

-- Use the function
local results = semantic_search("kb", "programming languages", 3)
return json.encode(results)
```

### Update Document

```lua
local json = require("cjson")

local function update_document(doc_id, new_text)
    -- Update text
    db:put("doc:" .. doc_id, new_text)

    -- Update embedding
    local emb = json.decode(plugins.embed.embed(new_text)).embedding

    -- Remove old vector and add new
    plugins.vdb.vdb_remove("kb", doc_id)
    plugins.vdb.vdb_add("kb", doc_id, emb)

    return "Updated: " .. doc_id
end

return update_document("1", "Python is a versatile programming language.")
```

## Index Management

### Rebuilding Index

```lua
local json = require("cjson")

-- Get all document IDs
local items = db:iterator()
local doc_ids = {}
for _, item in ipairs(items) do
    for key, _ in pairs(item) do
        if key:match("^doc:") then
            table.insert(doc_ids, key:match("^doc:(.+)$"))
        end
    end
end

-- Recreate index
plugins.vdb.vdb_create_index("kb_new", 384)

-- Re-index all documents
for _, doc_id in ipairs(doc_ids) do
    local text = db:get("doc:" .. doc_id)
    local emb = json.decode(plugins.embed.embed(text)).embedding
    plugins.vdb.vdb_add("kb_new", doc_id, emb)
end

return "Rebuilt index with " .. #doc_ids .. " documents"
```

## Best Practices

1. **Match dimensions**: Index dimension must match embedding model
2. **Use meaningful IDs**: IDs should map to your document storage
3. **Handle missing results**: Always check if results exist
4. **Index in batches**: For large datasets, process in batches

## Error Handling

```lua
local json = require("cjson")

local result = plugins.vdb.vdb_search("index", vector, 5)
local data = json.decode(result)

if data.status == "success" then
    return data.results
else
    return "Search failed: " .. (data.message or "Unknown error")
end
```
