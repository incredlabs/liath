# Vector Search & RAG

This tutorial covers semantic search and Retrieval-Augmented Generation (RAG) using Liath's embedding and vector search capabilities.

## Prerequisites

Install the required extras:

```bash
pip install liath[embed,vdb,llm]
```

## Overview

RAG combines:

1. **Embeddings**: Convert text to vector representations
2. **Vector Search**: Find similar documents by comparing vectors
3. **LLM**: Generate responses using retrieved context

## Basic Embedding

Generate embeddings from text:

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./rag_data")

# Generate an embedding
result = db.execute_lua('''
    local embedding = plugins.embed.embed("Hello, world!")
    return embedding
''')
print(f"Embedding dimension: {len(result)}")
```

## Creating a Vector Index

Set up a vector index for similarity search:

```python
# Create an index (dimension depends on embedding model)
db.execute_lua('''
    local result = plugins.vdb.vdb_create_index("documents", 384)
    return result
''')
```

## Indexing Documents

Store documents with their embeddings:

```python
documents = [
    {"id": "doc1", "text": "Python is a programming language."},
    {"id": "doc2", "text": "Machine learning uses algorithms to learn from data."},
    {"id": "doc3", "text": "Natural language processing analyzes human language."},
    {"id": "doc4", "text": "Deep learning is a subset of machine learning."},
]

for doc in documents:
    db.execute_lua(f'''
        -- Store the document text
        db:put("doc:{doc['id']}", "{doc['text']}")

        -- Generate embedding
        local embedding_json = plugins.embed.embed("{doc['text']}")
        local json = require("cjson")
        local embedding = json.decode(embedding_json).embedding

        -- Add to vector index
        plugins.vdb.vdb_add("documents", "{doc['id']}", embedding)

        return "Indexed: {doc['id']}"
    ''')
```

## Searching Similar Documents

Find documents similar to a query:

```python
query = "What is deep learning?"

result = db.execute_lua(f'''
    local json = require("cjson")

    -- Generate query embedding
    local query_embedding_json = plugins.embed.embed("{query}")
    local query_embedding = json.decode(query_embedding_json).embedding

    -- Search for similar documents
    local results = plugins.vdb.vdb_search("documents", query_embedding, 3)

    return results
''')

print("Similar documents:", result)
```

## Complete RAG Pipeline

Combine search and LLM for question answering:

```python
def ask_question(db, question):
    result = db.execute_lua(f'''
        local json = require("cjson")

        -- 1. Generate query embedding
        local query_json = plugins.embed.embed("{question}")
        local query_embedding = json.decode(query_json).embedding

        -- 2. Search for relevant documents
        local search_results = plugins.vdb.vdb_search("documents", query_embedding, 3)
        local results = json.decode(search_results)

        -- 3. Retrieve document content
        local context = ""
        for _, result in ipairs(results.results or {{}}) do
            local doc_text = db:get("doc:" .. result.id)
            if doc_text then
                context = context .. doc_text .. "\\n"
            end
        end

        -- 4. Generate answer using LLM
        local prompt = "Context:\\n" .. context .. "\\n\\nQuestion: {question}\\n\\nAnswer:"
        local response = plugins.llm.llm_complete(prompt)

        return response
    ''')
    return result

answer = ask_question(db, "What is the relationship between deep learning and machine learning?")
print(answer)
```

## Batch Embedding

Process multiple documents efficiently:

```python
texts = [
    "Document one content.",
    "Document two content.",
    "Document three content.",
]

result = db.execute_lua(f'''
    local json = require("cjson")
    local texts = json.decode('{json.dumps(texts)}')

    local embeddings = {{}}
    for i, text in ipairs(texts) do
        local emb_json = plugins.embed.embed(text)
        local emb = json.decode(emb_json).embedding
        embeddings[i] = emb
    end

    return json.encode(embeddings)
''')
```

## Using Different Models

Specify embedding models:

```python
# Use a specific model
result = db.execute_lua('''
    -- Check available models
    -- Default: BAAI/bge-small-en-v1.5

    local embedding = plugins.embed.embed("Sample text")
    return embedding
''')
```

## Vector Index Operations

### List Indexes

```python
result = db.execute_lua('''
    return plugins.vdb.vdb_list_indexes()
''')
```

### Remove from Index

```python
db.execute_lua('''
    plugins.vdb.vdb_remove("documents", "doc1")
    return "Removed doc1"
''')
```

### Get Index Info

```python
result = db.execute_lua('''
    return plugins.vdb.vdb_info("documents")
''')
```

## Example: Knowledge Base

Build a complete knowledge base:

```python
from liath import EmbeddedLiath
import json

class KnowledgeBase:
    def __init__(self, data_dir):
        self.db = EmbeddedLiath(data_dir=data_dir)
        self._init_index()

    def _init_index(self):
        self.db.execute_lua('''
            plugins.vdb.vdb_create_index("kb", 384)
            return "Index ready"
        ''')

    def add_document(self, doc_id, content):
        escaped_content = content.replace('"', '\\"')
        self.db.execute_lua(f'''
            local json = require("cjson")

            db:put("kb:{doc_id}", "{escaped_content}")

            local emb_json = plugins.embed.embed("{escaped_content}")
            local embedding = json.decode(emb_json).embedding

            plugins.vdb.vdb_add("kb", "{doc_id}", embedding)
            return "Added"
        ''')

    def search(self, query, top_k=5):
        result = self.db.execute_lua(f'''
            local json = require("cjson")

            local query_json = plugins.embed.embed("{query}")
            local query_emb = json.decode(query_json).embedding

            local results = plugins.vdb.vdb_search("kb", query_emb, {top_k})
            return results
        ''')
        return json.loads(result)

    def close(self):
        self.db.close()

# Usage
kb = KnowledgeBase("./kb_data")
kb.add_document("1", "Python is a programming language.")
kb.add_document("2", "Machine learning is a subset of AI.")
results = kb.search("programming languages")
print(results)
kb.close()
```

## Best Practices

1. **Chunk large documents**: Split documents into smaller chunks for better retrieval
2. **Use appropriate models**: Match embedding dimension to your use case
3. **Index management**: Create separate indexes for different content types
4. **Cache embeddings**: Store embeddings to avoid re-computation

## Clean Up

```python
db.close()
```

## Next Steps

- [LLM Plugin](../plugins/llm.md) - Language model details
- [Embeddings Plugin](../plugins/embed.md) - Embedding options
- [Vector DB Plugin](../plugins/vdb.md) - Vector search reference
