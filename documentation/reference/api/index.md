# API Reference

This section contains auto-generated API documentation from the Liath source code.

## Core Modules

- [liath](liath/index.md) - Main package exports
- [liath.database](liath/database.md) - Database class
- [liath.embedded](liath/embedded.md) - EmbeddedLiath class
- [liath.cli](liath/cli.md) - CLI implementation
- [liath.server](liath/server.md) - HTTP server

## Storage Backends

- [liath.storage.base](liath/storage/base.md) - StorageBase abstract class
- [liath.storage.leveldb_storage](liath/storage/leveldb_storage.md) - LevelDB backend
- [liath.storage.rocksdb_storage](liath/storage/rocksdb_storage.md) - RocksDB backend

## Plugin System

- [liath.plugin_base](liath/plugin_base.md) - PluginBase class
- [liath.plugins.db_plugin](liath/plugins/db_plugin.md) - Database operations
- [liath.plugins.embed_plugin](liath/plugins/embed_plugin.md) - Embeddings
- [liath.plugins.vdb_plugin](liath/plugins/vdb_plugin.md) - Vector database
- [liath.plugins.llm_plugin](liath/plugins/llm_plugin.md) - Language models
- [liath.plugins.file_plugin](liath/plugins/file_plugin.md) - File operations
- [liath.plugins.query_cache_plugin](liath/plugins/query_cache_plugin.md) - Query caching
- [liath.plugins.backup_restore_plugin](liath/plugins/backup_restore_plugin.md) - Backup/restore
- [liath.plugins.monitoring_logging_plugin](liath/plugins/monitoring_logging_plugin.md) - Monitoring

## Quick Links

### Main Classes

| Class | Description |
|-------|-------------|
| `EmbeddedLiath` | Simplified Python interface for embedding Liath |
| `Database` | Full-featured database class |
| `DatabaseCLI` | Command-line interface |
| `PluginBase` | Base class for plugins |

### Key Methods

| Method | Description |
|--------|-------------|
| `EmbeddedLiath.put(key, value)` | Store a value |
| `EmbeddedLiath.get(key)` | Retrieve a value |
| `EmbeddedLiath.delete(key)` | Delete a value |
| `EmbeddedLiath.execute_lua(query)` | Execute Lua code |
| `Database.execute_query(ns, query)` | Execute query in namespace |
| `Database.create_namespace(name)` | Create a namespace |
