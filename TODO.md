# Liath Project TODO List

## Project Overview
Liath is an AI-powered database system that combines key-value storage, vector search, and AI capabilities. It uses Lua as its query language and provides both CLI and HTTP interfaces.

## Current Status Assessment
The project has a solid foundation with:
- Dual storage backend support (RocksDB/LevelDB)
- Lua query language implementation
- Plugin architecture with several plugins already implemented
- CLI and HTTP server interfaces
- Basic namespace and user management
- LuaRocks package integration

Many features mentioned in the documentation are actually implemented as plugins, but may need refinement or full integration.

## High Priority Tasks

### 1. Core Database Features
- [ ] Implement vector search capabilities (beyond embedding generation)
- [ ] Add transaction support for LevelDB (currently only in RocksDB)
- [ ] Implement connection pooling for better concurrency
- [ ] Add proper data indexing mechanisms

### 2. Authentication & Security
- [ ] Implement proper password hashing (currently storing plain text)
- [ ] Add role-based access control
- [ ] Implement session management
- [ ] Add API key support
- [ ] Add rate limiting to HTTP API

## Medium Priority Tasks

### 3. Plugin System Enhancement
- [ ] Add plugin documentation
- [ ] Implement plugin lifecycle management
- [ ] Add plugin configuration support
- [ ] Create example usage scenarios for each plugin

### 4. Storage Improvements
- [ ] Add column family support for LevelDB (emulated)
- [ ] Implement data compression options
- [ ] Add data encryption at rest
- [ ] Implement data partitioning

### 5. CLI Enhancements
- [ ] Add command history persistence
- [ ] Implement auto-completion
- [ ] Add script file execution support
- [ ] Improve output formatting options

### 6. HTTP API Improvements
- [ ] Add RESTful endpoints for all database operations
- [ ] Implement proper JSON response handling
- [ ] Add CORS support
- [ ] Implement request/response validation

## Low Priority Tasks

### 7. Documentation & Examples
- [ ] Create comprehensive API documentation
- [ ] Add usage examples for all features
- [ ] Create tutorials for common use cases
- [ ] Add plugin development guide

### 8. Testing
- [ ] Add unit tests for all core components
- [ ] Implement integration tests
- [ ] Add performance benchmarks
- [ ] Create test suites for plugins

### 9. Deployment & Operations
- [ ] Add Docker support
- [ ] Create Kubernetes deployment manifests
- [ ] Add automated backup scheduling
- [ ] Implement health check endpoints

## Partially Implemented Features

The following features are mentioned in FEATURES.md and have partial implementations as plugins:
- [x] File operations (file_plugin.py)
- [x] AI integration (llm_plugin.py) - Local LLM and OpenAI support
- [x] Embedding generation (embed_plugin.py) - Using fastembed
- [x] Query caching (query_cache_plugin.py) - Using LRU cache
- [x] Monitoring (monitoring_logging_plugin.py) - Basic logging and stats
- [x] Backup & restore (backup_restore_plugin.py) - Basic file-based backup
- [ ] Vector search capabilities - Not fully implemented, only embedding generation

## Technical Debt

### 10. Code Quality Improvements
- [ ] Add proper error handling throughout the database layer
- [ ] Implement comprehensive logging instead of print statements
- [ ] Add type hints for better code documentation
- [ ] Refactor duplicated code (Lua environment setup)
- [ ] Improve code modularity and separation of concerns
- [ ] Add proper plugin interface documentation

### 11. Security Improvements
- [ ] Fix plaintext password storage in auth_db
- [ ] Add input validation and sanitization for all user inputs
- [ ] Implement proper authentication middleware for HTTP API
- [ ] Add security headers to HTTP responses
- [ ] Implement proper access controls for plugins

## Future Enhancements

### 12. Advanced Features
- [ ] Add support for more storage backends (e.g., SQLite, PostgreSQL)
- [ ] Implement distributed database capabilities
- [ ] Add support for graph database operations
- [ ] Implement time-series data handling
- [ ] Add support for streaming data ingestion
- [ ] Implement advanced vector search with similarity algorithms

### 13. Performance Optimizations
- [ ] Add query optimization engine
- [ ] Implement indexing mechanisms
- [ ] Add support for query parallelization
- [ ] Implement memory-efficient data structures
- [ ] Optimize plugin loading and initialization

## Contributing Guidelines
Please follow these steps when contributing:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for your changes
5. Update documentation as needed
6. Submit a pull request

## Getting Started
To start working on any of these tasks:
1. Clone the repository
2. Install dependencies using `poetry install`
3. Create the required directory structure: `mkdir -p data/default/{files,luarocks} plugins backups`
4. Run the setup script: `./liath/setup_luarocks.sh`
5. Choose a task from the list above and start implementing!

Note: For LLM functionality, you'll need to either:
- Download a GGUF model file for local inference, or
- Set the `OPENAI_API_KEY` environment variable for OpenAI integration
