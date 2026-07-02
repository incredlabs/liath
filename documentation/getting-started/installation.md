# Installation

This guide covers how to install Liath and its optional dependencies.

## Requirements

- Python 3.11 or higher
- pip or Poetry for package management

## Basic Installation

Install Liath from PyPI:

```bash
pip install liath
```

This installs the core package with LevelDB storage backend.

## Installation with Extras

Liath provides optional extras for additional features:

### Embeddings Support

For text and image embedding generation using FastEmbed:

```bash
pip install liath[embed]
```

### Vector Database Support

For vector similarity search using USearch:

```bash
pip install liath[vdb]
```

### LLM Integration

For language model access (OpenAI and local Llama):

```bash
pip install liath[llm]
```

### RocksDB Storage

For high-performance RocksDB storage backend:

```bash
pip install liath[rocksdb]
```

### All Features

Install everything:

```bash
pip install liath[embed,vdb,llm,rocksdb]
```

## Installation with Poetry

If you use Poetry for dependency management:

```bash
# Basic installation
poetry add liath

# With extras
poetry add liath[embed,vdb,llm]
```

## Development Installation

To install from source for development:

```bash
git clone https://github.com/incredlabs/liath.git
cd liath
poetry install

# Install with documentation tools
poetry install --with docs

# Install with all extras
poetry install --all-extras
```

## Verifying Installation

Verify the installation:

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./test_data")
db.put("test", "Hello, Liath!")
print(db.get("test"))  # Should print: Hello, Liath!
db.close()
```

Run from command line:

```bash
liath-cli --help
```

## Troubleshooting

### RocksDB Installation Issues

RocksDB requires system-level dependencies. On Ubuntu/Debian:

```bash
sudo apt-get install librocksdb-dev
```

On macOS with Homebrew:

```bash
brew install rocksdb
```

### LevelDB Installation Issues

LevelDB is typically installed automatically, but if you encounter issues:

```bash
# Ubuntu/Debian
sudo apt-get install libleveldb-dev

# macOS
brew install leveldb
```

### Lua Module Issues

If you need additional Lua modules, ensure LuaRocks is installed:

```bash
# Ubuntu/Debian
sudo apt-get install luarocks

# macOS
brew install luarocks
```
