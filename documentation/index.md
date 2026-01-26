# Liath

**A programmable key-value database with Lua query language and AI capabilities.**

Liath is an AI-powered database system that combines key-value storage with vector search and language model integration. It uses Lua as its query language and features a pluggable architecture for extensibility.

## Key Features

- **Pluggable Storage Backends**: Choose between RocksDB (high-performance) or LevelDB (lightweight)
- **Lua Query Language**: Write expressive queries using Lua scripting
- **Multi-Namespace Support**: Isolate data and contexts across namespaces
- **AI Integration**: Built-in support for embeddings, vector search, and LLM access
- **Plugin Architecture**: Extend functionality with custom plugins
- **Multiple Interfaces**: Use as a Python library, CLI tool, or HTTP API server

## Quick Example

```python
from liath import EmbeddedLiath

# Initialize the database
db = EmbeddedLiath(data_dir="./my_data")

# Basic key-value operations
db.put("greeting", "Hello, World!")
value = db.get("greeting")
print(value)  # Output: Hello, World!

# Execute Lua queries
result = db.execute_lua('return db:get("greeting")')
print(result)  # Output: Hello, World!

db.close()
```

## Use Cases

- **RAG (Retrieval-Augmented Generation)**: Store documents, generate embeddings, and perform semantic search
- **AI Agent Tool Storage**: Persistent memory for AI agents with structured queries
- **Batch Processing**: Efficient embedding generation for large datasets
- **Custom Data Pipelines**: Combine storage, search, and LLM capabilities in Lua scripts

## Installation

```bash
pip install liath
```

For AI features, install with extras:

```bash
pip install liath[embed,vdb,llm]
```

## Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed installation instructions
- [Quick Start](getting-started/quickstart.md) - Get up and running in 5 minutes
- [Tutorials](tutorials/basic-operations.md) - Learn Liath step by step
- [API Reference](reference/api/) - Complete API documentation
