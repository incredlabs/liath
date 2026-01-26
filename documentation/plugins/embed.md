# Embeddings Plugin (embed)

Generate text and image embeddings using FastEmbed models.

## Installation

```bash
pip install liath[embed]
```

## Functions

### plugins.embed.embed(text)

Generate an embedding for text.

**Parameters:**

- `text` (string): Text to embed

**Returns:** JSON string with embedding

**Example:**
```lua
local result = plugins.embed.embed("Hello, world!")
-- Returns: {"status": "success", "embedding": [0.1, 0.2, ...]}

local json = require("cjson")
local data = json.decode(result)
local embedding = data.embedding
return #embedding  -- Dimension (e.g., 384)
```

### plugins.embed.embed_batch(texts)

Generate embeddings for multiple texts.

**Parameters:**

- `texts` (table): Array of strings to embed

**Returns:** JSON string with embeddings array

**Example:**
```lua
local json = require("cjson")
local texts = {"Hello", "World", "Test"}
local result = plugins.embed.embed_batch(json.encode(texts))
local data = json.decode(result)
return #data.embeddings  -- 3
```

## Models

The default model is `BAAI/bge-small-en-v1.5` with 384 dimensions.

Available models include:

| Model | Dimensions | Description |
|-------|------------|-------------|
| BAAI/bge-small-en-v1.5 | 384 | Fast, lightweight English |
| BAAI/bge-base-en-v1.5 | 768 | Balanced quality/speed |
| BAAI/bge-large-en-v1.5 | 1024 | High quality English |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | Popular general-purpose |

## Usage Examples

### Store Document with Embedding

```lua
local json = require("cjson")

-- Generate embedding
local text = "Machine learning is a subset of artificial intelligence."
local result = plugins.embed.embed(text)
local data = json.decode(result)

-- Store document and embedding
db:put("doc:1:text", text)
db:put("doc:1:embedding", json.encode(data.embedding))

return "Document stored"
```

### Batch Processing

```lua
local json = require("cjson")

local documents = {
    "Python is a programming language.",
    "Machine learning uses algorithms.",
    "Data science combines statistics and programming."
}

for i, doc in ipairs(documents) do
    local result = plugins.embed.embed(doc)
    local data = json.decode(result)

    db:put("doc:" .. i .. ":text", doc)
    db:put("doc:" .. i .. ":embedding", json.encode(data.embedding))
end

return "Processed " .. #documents .. " documents"
```

### Semantic Similarity

```lua
local json = require("cjson")

-- Helper function for cosine similarity
local function cosine_similarity(a, b)
    local dot = 0
    local norm_a = 0
    local norm_b = 0

    for i = 1, #a do
        dot = dot + a[i] * b[i]
        norm_a = norm_a + a[i] * a[i]
        norm_b = norm_b + b[i] * b[i]
    end

    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))
end

-- Compare two texts
local text1 = "The cat sat on the mat."
local text2 = "A feline rested on the rug."

local emb1 = json.decode(plugins.embed.embed(text1)).embedding
local emb2 = json.decode(plugins.embed.embed(text2)).embedding

local similarity = cosine_similarity(emb1, emb2)
return string.format("Similarity: %.4f", similarity)
```

## Best Practices

1. **Batch when possible**: Use `embed_batch` for multiple texts
2. **Cache embeddings**: Store embeddings to avoid recomputation
3. **Match dimensions**: Ensure vector index dimension matches model
4. **Chunk large texts**: Split long documents into smaller chunks

## Error Handling

```lua
local result = plugins.embed.embed("text")
local json = require("cjson")
local data = json.decode(result)

if data.status == "success" then
    return data.embedding
else
    return "Error: " .. (data.message or "Unknown error")
end
```
